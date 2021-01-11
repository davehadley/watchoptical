#!/usr/bin/env bash

if [ -n "$BASH_SOURCE" ]; then
  script=$BASH_SOURCE
elif [ -n "$ZSH_VERSION" ]; then
  setopt function_argzero
  script=$0
elif eval '[[ -n ${.sh.file} ]]' 2>/dev/null; then
  eval 'script=${.sh.file}'
else
  script=./
fi
scriptdir=$(dirname ${script})

if [ -z "${WORKSPACE}" ];
then
    WATCHOPTICALWORKSPACE=$(CDPATH= cd -- "${scriptdir}" && pwd -P)
else
    WATCHOPTICALWORKSPACE=${WORKSPACE}
fi

CONDABIN=${WATCHOPTICALWORKSPACE}/miniconda/bin
CONDAACTIVATE=${CONDABIN}/activate
CONDA=${CONDABIN}/conda

# If conda is not installed, download miniconda
if ! command -v ${CONDA} &> /dev/null
then
    echo "conda not found at ${CONDA}"
    WATCHOPTICALMINICONDA=${WATCHOPTICALWORKSPACE}/miniconda
    if [ ! -d "${WATCHOPTICALMINICONDA}" ]
    then
        echo "Downloading miniconda..."
        case "$(uname -s)" in
            Darwin*)    OSKIND=MacOSX;;
            *)          OSKIND=Linux;;
        esac
        echo "Detected OS = ${OSKIND}"
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-${OSKIND}-x86_64.sh -nv -O miniconda.sh
        bash miniconda.sh -b -p ${WATCHOPTICALMINICONDA}
        source ${WATCHOPTICALMINICONDA}/bin/activate
        ${CONDA} config --set always_yes yes
        ${CONDA} config --set env_prompt '({name}) '
        ${CONDA} update -q conda
    fi
    source ${WATCHOPTICALMINICONDA}/bin/activate
    if ! command -v ${CONDA} &> /dev/null
    then
        echo "ERROR: cannot find conda command!"
    fi
fi

# If environment does not exist, create it
WATCHOPTICALCONDAENV=${WATCHOPTICALWORKSPACE}/env/WATCHOPTICAL
if [ ! -d "${WATCHOPTICALCONDAENV}" ]
then 
    ${CONDA} env create -f environment.yml --prefix ${WATCHOPTICALCONDAENV}
fi

# Activate the environment
source ${CONDAACTIVATE}
#${CONDA} activate ${WATCHOPTICALCONDAENV}
source activate ${WATCHOPTICALCONDAENV}