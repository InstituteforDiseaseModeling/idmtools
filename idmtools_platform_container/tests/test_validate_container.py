"""
Unit tests for validate_container_running function.

Tests cover:
- New image pulled, old container stopped and new one started
- Running container with current image reused
- Running container with old image stopped, new one started
- Mount check: container with empty mount stopped
- Mount check: container with populated mount reused
- Stopped container with current image restarted
- Stopped container with old image removed, new one started
- force_start stops all containers and starts new
- new_container flag always starts new container
- Windows skips mount check
- No containers found, new one started
- Image pull failure exits
"""

import unittest
from unittest.mock import MagicMock, patch, call
import platform as sys_platform
from idmtools_platform_container.container_operations.docker_operations import validate_container_running


# ---------------------------------------------------------------------------
# Helpers to build mock containers
# ---------------------------------------------------------------------------

def make_mock_container(short_id, image_id, status="running"):
    container = MagicMock()
    container.short_id = short_id
    container.attrs = {"Image": image_id}
    container.status = status
    return container


def make_mock_image(image_id):
    image = MagicMock()
    image.id = image_id
    return image


def make_mock_platform(
    docker_image="myimage:latest",
    force_start=False,
    new_container=False,
    container_prefix=None,
    include_stopped=False,
    data_mount="/home/container_data",
):
    platform = MagicMock()
    platform.docker_image = docker_image
    platform.force_start = force_start
    platform.new_container = new_container
    platform.container_prefix = container_prefix
    platform.include_stopped = include_stopped
    platform.data_mount = data_mount
    return platform


# ---------------------------------------------------------------------------
# The module path to patch — adjust to match your actual module path
# ---------------------------------------------------------------------------
MODULE = "idmtools_platform_container.container_operations.docker_operations"

class TestValidateContainerRunning(unittest.TestCase):

    # ------------------------------------------------------------------
    # 1. No running or stopped containers → start new
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_no_containers_starts_new(
        self, mock_check, mock_pull, mock_stop_all, mock_docker,
        mock_get_container, mock_sys_platform
    ):

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = []
        platform.start_container.return_value = "new123"

        result = validate_container_running(platform)

        platform.start_container.assert_called_once()
        self.assertEqual(result, "new123")

    # ------------------------------------------------------------------
    # 2. Running container with CURRENT image → reuse it
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_running_container_current_image_reused(
        self, mock_check, mock_pull, mock_sort,
        mock_stop_all, mock_docker, mock_get_container, mock_sys_platform
    ):

        current_image_id = "sha256:abc123"
        container = make_mock_container("ctr001", current_image_id)

        mock_sort.return_value = [container]
        mock_get_container.return_value = container

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        # Simulate populated mount (exists)
        mock_sys_platform.system.return_value = "Linux"
        exec_result = MagicMock()
        exec_result.output = b"exists"
        container.exec_run.return_value = exec_result

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [("running", container)]

        result = validate_container_running(platform)

        platform.start_container.assert_not_called()
        self.assertEqual(result, "ctr001")

    # ------------------------------------------------------------------
    # 3. Running container with OLD image → stop it, start new
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.stop_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_running_container_old_image_stopped_new_started(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_stop_container, mock_get_container, mock_sys_platform
    ):

        old_image_id = "sha256:old000"
        current_image_id = "sha256:new111"
        container = make_mock_container("ctr_old", old_image_id)

        mock_sort.return_value = [container]
        mock_get_container.return_value = container

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        mock_sys_platform.system.return_value = "Linux"

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [("running", container)]
        platform.start_container.return_value = "new_ctr"

        result = validate_container_running(platform)

        mock_stop_container.assert_called_once_with("ctr_old", remove=True)
        platform.start_container.assert_called_once()
        self.assertEqual(result, "new_ctr")

    # ------------------------------------------------------------------
    # 4. Mount check: empty mount → stop container, start new (Linux)
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.stop_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_empty_mount_stops_container_starts_new(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_stop_container, mock_get_container, mock_sys_platform
    ):

        current_image_id = "sha256:abc123"
        container = make_mock_container("ctr002", current_image_id)

        mock_sort.return_value = [container]
        mock_get_container.return_value = container

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        # Simulate empty mount (not_exists)
        mock_sys_platform.system.return_value = "Linux"
        exec_result = MagicMock()
        exec_result.output = b"not_exists"
        container.exec_run.return_value = exec_result

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [("running", container)]
        platform.start_container.return_value = "new_ctr"

        result = validate_container_running(platform)

        mock_stop_container.assert_called_once_with("ctr002", remove=True)
        platform.start_container.assert_called_once()
        self.assertEqual(result, "new_ctr")

    # ------------------------------------------------------------------
    # 5. Windows skips mount check → reuse container
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_windows_skips_mount_check(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_get_container, mock_sys_platform
    ):

        current_image_id = "sha256:abc123"
        container = make_mock_container("ctr_win", current_image_id)

        mock_sort.return_value = [container]
        mock_get_container.return_value = container

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        mock_sys_platform.system.return_value = "Windows"

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [("running", container)]

        result = validate_container_running(platform)

        # exec_run should NOT be called (mount check skipped on Windows)
        container.exec_run.assert_not_called()
        platform.start_container.assert_not_called()
        self.assertEqual(result, "ctr_win")

    # ------------------------------------------------------------------
    # 6. Stopped container with CURRENT image → restart it
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_stopped_container_current_image_restarted(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_get_container, mock_sys_platform
    ):

        current_image_id = "sha256:abc123"
        container = make_mock_container("ctr_stopped", current_image_id, status="exited")

        mock_sort.return_value = [container]

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [("exited", container)]

        result = validate_container_running(platform)

        container.restart.assert_called_once()
        platform.start_container.assert_not_called()
        self.assertEqual(result, "ctr_stopped")

    # ------------------------------------------------------------------
    # 7. Stopped container with OLD image → remove it, start new
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.stop_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_stopped_container_old_image_removed_new_started(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_stop_container, mock_get_container, mock_sys_platform
    ):

        old_image_id = "sha256:old000"
        current_image_id = "sha256:new111"
        container = make_mock_container("ctr_old_stopped", old_image_id, status="exited")

        mock_sort.return_value = [container]

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [("exited", container)]
        platform.start_container.return_value = "new_ctr"

        result = validate_container_running(platform)

        mock_stop_container.assert_not_called()
        container.restart.assert_not_called()
        platform.start_container.assert_called_once()
        self.assertEqual(result, "new_ctr")

    # ------------------------------------------------------------------
    # 8. force_start=True → stop all containers, start new
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_force_start_stops_all_starts_new(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_get_container, mock_sys_platform
    ):

        container = make_mock_container("ctr_running", "sha256:abc")
        mock_sort.return_value = [container]

        platform = make_mock_platform(force_start=True)
        platform.retrieve_match_containers.return_value = [("running", container)]
        platform.start_container.return_value = "forced_new"

        result = validate_container_running(platform)

        self.assertTrue(mock_stop_all.called)
        platform.start_container.assert_called_once()
        self.assertEqual(result, "forced_new")

    # ------------------------------------------------------------------
    # 9. new_container=True → always start new, ignore existing
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_new_container_flag_always_starts_new(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_get_container, mock_sys_platform
    ):

        container = make_mock_container("ctr_existing", "sha256:abc")
        mock_sort.return_value = [container]

        platform = make_mock_platform(new_container=True)
        platform.retrieve_match_containers.return_value = [("running", container)]
        platform.start_container.return_value = "brand_new"

        result = validate_container_running(platform)

        platform.start_container.assert_called_once()
        self.assertEqual(result, "brand_new")

    # ------------------------------------------------------------------
    # 10. Image pull failure → exit(-1)
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=False)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_image_pull_failure_exits(self, mock_check, mock_pull):

        platform = make_mock_platform()

        with self.assertRaises(SystemExit):
            validate_container_running(platform)

    # ------------------------------------------------------------------
    # 11. Image not local → pulls it, then proceeds
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.pull_docker_image", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=False)
    def test_image_not_local_pulls_then_starts(
        self, mock_check, mock_pull, mock_stop_all,
        mock_docker, mock_get_container, mock_sys_platform
    ):

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = []
        platform.start_container.return_value = "pulled_new"

        result = validate_container_running(platform)

        mock_pull.assert_called_once_with(platform.docker_image)
        platform.start_container.assert_called_once()
        self.assertEqual(result, "pulled_new")

    # ------------------------------------------------------------------
    # 12. Multiple running containers, first has old image, second is current
    # ------------------------------------------------------------------
    @patch(f"{MODULE}.sys_platform")
    @patch(f"{MODULE}.get_container")
    @patch(f"{MODULE}.stop_container")
    @patch(f"{MODULE}.docker")
    @patch(f"{MODULE}.stop_all_containers")
    @patch(f"{MODULE}.sort_containers_by_start")
    @patch(f"{MODULE}.pull_docker_image_if_changed", return_value=True)
    @patch(f"{MODULE}.check_local_image", return_value=True)
    def test_multiple_containers_picks_current_image(
        self, mock_check, mock_pull, mock_sort, mock_stop_all,
        mock_docker, mock_stop_container, mock_get_container, mock_sys_platform
    ):

        old_image_id = "sha256:old000"
        current_image_id = "sha256:new111"

        old_container = make_mock_container("ctr_old", old_image_id)
        new_container = make_mock_container("ctr_new", current_image_id)

        mock_sort.return_value = [old_container, new_container]
        mock_get_container.side_effect = lambda cid: (
            old_container if cid == "ctr_old" else new_container
        )

        mock_image = make_mock_image(current_image_id)
        mock_docker.from_env.return_value.images.get.return_value = mock_image

        mock_sys_platform.system.return_value = "Linux"
        exec_result = MagicMock()
        exec_result.output = b"exists"
        new_container.exec_run.return_value = exec_result

        platform = make_mock_platform()
        platform.retrieve_match_containers.return_value = [
            ("running", old_container),
            ("running", new_container),
        ]

        result = validate_container_running(platform)

        # Old container should be stopped
        mock_stop_container.assert_called_with("ctr_old", remove=True)
        # New container should be reused
        self.assertEqual(result, "ctr_new")
        platform.start_container.assert_not_called()


if __name__ == "__main__":
    unittest.main()