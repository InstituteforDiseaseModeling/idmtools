import unittest
from unittest.mock import MagicMock, patch
from docker.errors import ImageNotFound, APIError as DockerAPIError

from idmtools_platform_container.container_operations.docker_operations import check_local_image, pull_docker_image, \
    pull_docker_image_if_changed


class TestCheckLocalImage(unittest.TestCase):

    @patch('docker.from_env')
    def test_image_exists(self, mock_docker):
        mock_docker().images.get.return_value = MagicMock()
        self.assertTrue(check_local_image('myimage:latest'))

    @patch('docker.from_env')
    def test_image_not_found(self, mock_docker):
        mock_docker().images.get.side_effect = ImageNotFound('not found')
        self.assertFalse(check_local_image('myimage:latest'))

    @patch('docker.from_env')
    def test_appends_latest_tag(self, mock_docker):
        mock_docker().images.get.return_value = MagicMock()
        check_local_image('myimage')
        mock_docker().images.get.assert_called_with('myimage:latest')


class TestPullDockerImage(unittest.TestCase):

    @patch('docker.from_env')
    def test_pull_success(self, mock_docker):
        mock_docker().images.pull.return_value = MagicMock()
        self.assertTrue(pull_docker_image('myimage:latest'))

    @patch('docker.from_env')
    def test_pull_failure(self, mock_docker):
        mock_docker().images.pull.side_effect = DockerAPIError('pull failed')
        self.assertFalse(pull_docker_image('myimage:latest'))

    @patch('docker.from_env')
    def test_appends_tag_if_missing(self, mock_docker):
        mock_docker().images.pull.return_value = MagicMock()
        pull_docker_image('myimage')
        mock_docker().images.pull.assert_called_with('myimage:latest')

    @patch('docker.from_env')
    def test_uses_provided_tag(self, mock_docker):
        mock_docker().images.pull.return_value = MagicMock()
        pull_docker_image('myimage', tag='v1.0')
        mock_docker().images.pull.assert_called_with('myimage:v1.0')


class TestPullDockerImageIfChanged(unittest.TestCase):

    def _make_client(self, mock_docker, local_digests, server_digest):
        client = mock_docker()
        local_image = MagicMock()
        local_image.attrs = {'RepoDigests': local_digests}
        client.images.get.return_value = local_image

        registry_data = MagicMock()
        registry_data.attrs = {'Descriptor': {'digest': server_digest}}
        client.images.get_registry_data.return_value = registry_data
        return client

    @patch('docker.from_env')
    def test_same_digest_skips_pull(self, mock_docker):
        digest = 'sha256:abc123'
        self._make_client(mock_docker, [f'myimage@{digest}'], digest)
        result = pull_docker_image_if_changed('myimage:latest')
        self.assertTrue(result)
        mock_docker().images.pull.assert_not_called()

    @patch('idmtools_platform_container.container_operations.docker_operations.pull_docker_image')
    @patch('docker.from_env')
    def test_different_digest_pulls(self, mock_docker, mock_pull):
        self._make_client(mock_docker, ['myimage@sha256:olddigest'], 'sha256:newdigest')
        mock_pull.return_value = True
        result = pull_docker_image_if_changed('myimage:latest')
        self.assertTrue(result)
        mock_pull.assert_called_once_with('myimage:latest')

    @patch('docker.from_env')
    def test_registry_unreachable_returns_true(self, mock_docker):
        # If registry is down, we should safely use the local image
        client = mock_docker()
        local_image = MagicMock()
        local_image.attrs = {'RepoDigests': ['myimage@sha256:abc123']}
        client.images.get.return_value = local_image
        client.images.get_registry_data.side_effect = DockerAPIError('unreachable')
        result = pull_docker_image_if_changed('myimage:latest')
        self.assertTrue(result)

    @patch('idmtools_platform_container.container_operations.docker_operations.pull_docker_image')
    @patch('docker.from_env')
    def test_empty_local_digests_pulls(self, mock_docker, mock_pull):
        # Locally built image with no RepoDigests — always re-pull
        self._make_client(mock_docker, [], 'sha256:newdigest')
        mock_pull.return_value = True
        pull_docker_image_if_changed('myimage:latest')
        mock_pull.assert_called_once()


if __name__ == '__main__':
    unittest.main()
