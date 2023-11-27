

export PY=python.exe
export DEF_PATH=/home/jbk/jimk/MAGIS-100
export DEF_CODE=$DEF_PATH/read_stuff/python
: ${MAGIS_PATH:=$DEF_PATH}
: ${MAGIS_CODE:=$DEF_CODE}
export XER_HOME=$MAGIS_PATH/XER_files
export SCHED_HOME=$MAGIS_PATH/read_stuff/input
export EXTRACT_HOME=$MAGIS_PATH/read_stuff/extracted
DO_COPY='n'

if [ $# -eq 0 ] 
then
    echo "Usage: $0 [-c XER_name] -n schedule_name"
    echo " -c : copy the exported XER file \$XER_HOME/<XER_name>.xer> to \$SCHED_HOME"
    echo " -n : name for this schedule, \$SCHED_HOME/schedule_<name>.xer"
    echo " example schedule names:  current, WS2309, BL2307"
    echo " example XER names: MAGIS100BL-BCR, MAGIS100WS-2309"
    echo " data is extracted to \$EXTRACT_HOME/tab_*_<name>.csv"
    echo " SCHED_HOME=${SCHED_HOME}"
    echo " XER_HOME=${XER_HOME}"
    echo " EXTRACTED_HOME=${EXTRACT_HOME}"
    echo " \$MAGIS_PATH default is ${DEF_PATH}"
    echo " \$MAGIS_CODE default is ${DEF_CODE}"
    exit 1
fi

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--copy)
      XER_NAME="$2"
      DO_COPY='y'
      shift 2 
      ;;
    -n|--name)
      SCHED_NAME="$2"
      shift 2
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

if [ $DO_COPY == 'y' ]
then
    cp $XER_HOME/$XER_NAME.xer $SCHED_HOME/schedule_$SCHED_NAME.xer
fi

$PY ./xer_extractor.py -x $SCHED_NAME
$PY ./reader.py -d -x $SCHED_NAME -S

