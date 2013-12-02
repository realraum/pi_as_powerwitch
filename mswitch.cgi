#!/bin/sh

VALID_ONOFF_IDS="4 17 18 21 22 23"
GPIOPATH=/sys/class/gpio/gpio

for QUERY in `echo $QUERY_STRING | tr '&' ' '`; do
  for VALIDID in $VALID_ONOFF_IDS; do
    if [ "$QUERY" = "$VALIDID=1" ]; then
      eval "GPIO_$VALIDID"=1
    elif [ "$QUERY" = "$VALIDID=0" ]; then
      eval "GPIO_$VALIDID=0"
    elif [ "$QUERY" = "$VALIDID=q" ]; then
      eval "GPIO_$VALIDID=q"
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
  if [ "$GPIOVALUE" = "0" ]; then
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

echo "{"
for CHECKID in $VALID_ONOFF_IDS; do
  VAL=""
  VAL="$(eval echo \$GPIO_$CHECKID)"
  [ -z $VAL ] && continue
  if [ $VAL = 1 -o $VAL = 0 ]; then
    [ $VAL = 1 ] && VAL=0 || VAL=1
    echo "$VAL" > "${GPIOPATH}${CHECKID}/value"
  fi
  echo -n "\"$CHECKID\":"
  print_gpio_state $CHECKID
  echo ","
done
echo "\"-1\":false}"
#      echo "<html>"
#      echo "<head>"
#      echo "<title>Realraum Relay Switch</title>"
#      echo '<script type="text/javascript">window.location="/cgi-bin/switch.cgi";</script>'
#      echo "</head></html>"
#      exit 0

