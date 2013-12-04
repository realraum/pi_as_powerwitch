#!/bin/zsh

VALID_ONOFF_IDS=(4 17 18 21 22 23)
GPIOPATH=/sys/class/gpio/gpio
local -A GPIOS
for QUERY in `echo $QUERY_STRING | tr '&' ' '`; do
  for VALIDID in $VALID_ONOFF_IDS; do
    if [ "$QUERY" = "$VALIDID=1" ]; then
      GPIOS[$VALIDID]=1
    elif [ "$QUERY" = "$VALIDID=0" ]; then
      GPIOS[$VALIDID]=0
    fi
  done
  if [ "$QUERY" = "mobile=1" ]; then
    MOBILE='1'
    NOFLOAT='1'
  elif [ "$QUERY" = "nofloat=1" ]; then
    NOFLOAT='1'
  fi
done


print_gpio_state() {
  GPIOVALUE=$(cat "${GPIOPATH}${1}/value")
  if [[ $GPIOVALUE == "0" ]]; then
    echo -n "true"
  else
    echo -n "false"
  fi
}

gpio_is_on() {
  GPIOVALUE=$(cat "${GPIOPATH}${1}/value")
  [ "$GPIOVALUE" = "0" ]
}

echo "Content-type: text/html"
echo ""

local -a GPIOSTATES
for CHECKID in $VALID_ONOFF_IDS; do
  VAL=$GPIOS[$CHECKID]
  if [[ $VAL == 1 || $VAL == 0 ]]; then
    [[ $VAL == 1 ]] && VAL=0 || VAL=1
    echo "$VAL" > "${GPIOPATH}${CHECKID}/value"
  fi
  GPIOSTATES+=(\"${CHECKID}\":"$(print_gpio_state $CHECKID)")
done
JSON_STATE="{${(j:,:)GPIOSTATES}}"
print ${(q)JSON_STATE}
if ((#GPIOS > 0)); then
  print "[$(date +%s),\"$REMOTE_ADDR\",${(q)JSON_STATE}]," >> /var/log/licht/mswitch.log
fi
