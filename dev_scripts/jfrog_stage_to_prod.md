<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->



<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Windows:
1. install jfrog cli:
    1). Download the latest jfrog in windows powershell:
    `powershell "Start-Process -Wait -Verb RunAs powershell '-NoProfile iwr https://releases.jfrog.io/artifactory/jfrog-cli/v2-jf/[RELEASE]/jfrog-cli-windows-amd64/jf.exe -OutFile $env:SYSTEMROOT\system32\jf.exe'"; jf intro`
    2). `jf login`, After logging in via your web browser, please enter the code if prompted: xxxx
    3). `jf c add`
        Enter a unique server identifier: idm-jfrog
    4). `jf config show`
        Server ID:                      idm-jfrog
        JFrog Platform URL:             https://packages.idmod.org/
        Artifactory URL:                https://packages.idmod.org/artifactory/
        Distribution URL:               https://packages.idmod.org/distribution/
        Xray URL:                       https://packages.idmod.org/xray/
        Mission Control URL:            https://packages.idmod.org/mc/
        Pipelines URL:                  https://packages.idmod.org/pipelines/
        User:                           shchen@idmod.org
        Access token:                   *** (Subject: 'jfac@01cp6fjfepephg11sgme9w08aw/users/shchen@idmod.org')
        Refresh token:                  ***
        Default:                        true

2. Run following script in powershell to copy all packages from staging to production (copy & paste):

$packages = @{
    "idmtools"               = "idmtools"
    "idmtools-cli"           = "idmtools_cli"
    "idmtools-models"        = "idmtools_models"
    "idmtools-platform-comps" = "idmtools_platform_comps"
	"idmtools-platform-general"               = "idmtools_platform_general"
    "idmtools-platform-container"           = "idmtools_platform_container"
    "idmtools-platform-slurm"        = "idmtools_platform_slurm"
    "idmtools-test" = "idmtools_test"
}

foreach ($distName in $packages.Keys) {
    $fileName = $packages[$distName]
    $version = "2.2.2"

    jf rt cp "idm-pypi-staging/$distName/$version/$fileName-$version.tar.gz" `
                 "idm-pypi-production/$distName/$version/" --flat=true --dry-run

    jf rt cp "idm-pypi-staging/$distName/$version/$fileName-$version-py3-none-any.whl" `
                 "idm-pypi-production/$distName/$version/" --flat=true --dry-run
}

3. Remove the --dry-run flag from step 2 once the results look correct for all packages.
{
  "status": "success",
  "totals": {
    "success": 1,
    "failure": 0
  }
}