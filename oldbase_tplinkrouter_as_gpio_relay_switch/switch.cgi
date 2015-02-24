#!/bin/sh

for QUERY in `echo $QUERY_STRING | tr '&' ' '`; do
  for VALUE in `echo $QUERY | tr '=' ' '`; do
    if [ "$VALUE" == "id" ]; then
      ID='?'
    elif [ "$ID" == "?" ]; then
      ID=$VALUE
    elif [ "$VALUE" == "power" ]; then
      POWER='?'
    elif [ "$POWER" == "?" ]; then
      POWER=$VALUE
    elif [ "$VALUE" == "mobile" ]; then
      MOBILE='1'
      NOFLOAT='1'
    elif [ "$VALUE" == "nofloat" ]; then
      NOFLOAT='1'
    fi
    i=$i+1
  done
done


GPIOPATH=/sys/class/gpio/gpio
#VALID_ONOFF_IDS="7 18 20 29"
VALID_ONOFF_IDS="7 18 20"
VALID_SEND_IDS=""

print_gpio_state() {
  GPIOVALUE=$(cat "${GPIOPATH}${1}/value")
  if [ "$GPIOVALUE" = "1" ]; then
    echo "ON"
  else
    echo "Off"
  fi
}

gpio_is_on() {
  GPIOVALUE=$(cat "${GPIOPATH}${1}/value")
  [ "$GPIOVALUE" = "1" ]
}

if [ "$POWER" == "1" -o "$POWER" == "0" ]; then
  for CHECKID in $VALID_ONOFF_IDS ; do
    if [ "$CHECKID" == "$ID" ]; then
      echo "$POWER" > "${GPIOPATH}${ID}/value"
      echo "Content-type: text/html"
      echo ""
      echo "<html>"
      echo "<head>"
      echo "<title>Realraum Relay Switch</title>"
      echo '<script type="text/javascript">window.location="/cgi-bin/switch.cgi";</script>'
      echo "</head></html>"
      exit 0
    fi
  done
fi

DESC_7="Decke Links Vorne"
DESC_20="Decke Rechts Vorne"
DESC_18="Decke Rechts Mitte"
#DESC_29="GPIO Nicht Belegt"

echo "Content-type: text/html"
echo ""
echo "<html>"
echo "<head>"
echo "<title>Realraum Relay Power</title>"
echo '<script type="text/javascript">'

echo 'function callbackUpdateButtons(req) {
  if (req.status != 200) {
    return;
  }
  var data = JSON.parse(req.responseText);
  for (var keyid in data) {
    on_btn = document.getElementById("onbtn_"+keyid);
    off_btn = document.getElementById("offbtn_"+keyid);
    if (on_btn && off_btn)
    {
      on_btn.className = "onbutton";
      off_btn.className = "offbutton";
      if (data[keyid])
      { on_btn.className += " enableborder"; }
      else
      { off_btn.className += " enableborder"; }
    }
  }
}'

echo 'function updateButtons(uri) {
  var req = new XMLHttpRequest;
  req.overrideMimeType("application/json");
  req.open("GET", uri, true);
  req.onload  = function() {callbackUpdateButtons(req)};
  req.setRequestHeader("googlechromefix","");
  req.send(null);
}'

echo 'function sendMultiButton( str ) {
 url = "/cgi-bin/mswitch.cgi?"+str;
  updateButtons(url);
}'

echo 'setInterval("updateButtons(\"/cgi-bin/mswitch.cgi\");", 30*1000);'

echo 'function sendButton( onoff, btn )'
echo '{'
echo ' var req = new XMLHttpRequest();'
echo ' url = "/cgi-bin/switch.cgi?power="+onoff+"&id="+btn;'
echo ' req.open("GET", url ,false);'
echo ' //google chrome workaround'
echo ' req.setRequestHeader("googlechromefix","");'
echo ' req.send(null);'
echo '}'
echo '</script>'
echo '<style>'
echo 'div.switchbox {'
echo '    float:left;'
echo '    margin:2px;'
#echo '    max-width:236px;'
echo '    max-width:300px;'
echo '    font-size:10pt;'
echo '    border:1px solid black;'
#echo '    height: 32px;'
echo '    padding:0;'
echo '}'

echo 'div.switchnameleft {'
echo '    width:12em; display:inline-block; vertical-align:middle; margin-left:3px;'
echo '}'

echo 'span.alignbuttonsright {'
echo '    top:0px; float:right; display:inline-block; text-align:right; padding:0;'
echo '}'

echo 'div.switchnameright {'
echo '    width:12em; display:inline-block; vertical-align:middle; float:right; display:inline-block; margin-left:1ex; margin-right:3px; margin-top:3px; margin-bottom:3px;'
echo '}'

echo 'span.alignbuttonsleft {'
echo '    float:left; text-align:left; padding:0;'
echo '}'

echo '.onbutton {'
echo '    font-size:11pt;'
echo '    width: 40px;'
echo '    height: 32px;'
echo '    background-color: lime;'
echo '    margin: 0px;'
echo '}'

echo '.offbutton {'
echo '    font-size:11pt;'
echo '    width: 40px;'
echo '    height: 32px;'
echo '    background-color: red;'
echo '    margin: 0px;'
echo '}'

echo '.sendbutton {'
echo '    font-size:11pt;'
echo '    width: 40px;'
echo '    height: 32px;'
#echo '    background-color: grey;'
echo '    margin: 0px;'
echo '}'

echo '.enableborder {
    font-weight: bold;
    font-variant: small-caps;
    border-style: inset;'
echo '}'
echo '</style>'
echo "</head>"
echo "<body>"
#echo "<h1>Realraum rf433ctl</h1>"
#echo "<div style=\"float:left; border:1px solid black;\">"
echo "<div style=\"float:left;\">"
echo "<div style=\"float:left; border:1px solid black; margin-right:2ex; margin-bottom:2ex;\">"
for DISPID in $VALID_ONOFF_IDS; do
  NAME="$(eval echo -n \$DESC_$DISPID)"
  [ -z "$NAME" ] && NAME=$DISPID

  echo "<div class=\"switchbox\">"
  echo "<span class=\"alignbuttonsleft\">"
  if gpio_is_on $DISPID; then
  echo " <button id=\"onbtn_$DISPID\" class=\"onbutton enableborder\" onClick='sendMultiButton(\"$DISPID=1\");'>On</button>"
  echo " <button id=\"offbtn_$DISPID\" class=\"offbutton\" onClick='sendMultiButton(\"$DISPID=0\");'>Off</button>"
  else
  echo " <button id=\"onbtn_$DISPID\" class=\"onbutton\" onClick='sendMultiButton(\"$DISPID=1\");'>On</button>"
  echo " <button id=\"offbtn_$DISPID\" class=\"offbutton enableborder\" onClick='sendMultiButton(\"$DISPID=0\");'>Off</button>"
  fi
  echo "</span>"
  echo -n "<div class=\"switchnameright\">$NAME</div>"
#  echo -n "<div class=\"switchnameright\">$NAME ("
#  print_gpio_state $DISPID
#  echo ")</div>"
  echo "</div>"

  if [ "$NOFLOAT" == "1" ]; then
    echo "<br/>"
  fi
done

echo "<div class=\"switchbox\">"
echo "<span class=\"alignbuttonsleft\">"
echo -n " <button class=\"onbutton\" onClick='sendMultiButton(\""
for DISPID in $VALID_ONOFF_IDS; do echo -n "$DISPID=1&"; done
echo "\");'>On</button>"
echo -n " <button class=\"offbutton\" onClick='sendMultiButton(\""
for DISPID in $VALID_ONOFF_IDS; do echo -n "$DISPID=0&"; done
echo "\");'>Off</button>"
echo "</span>"
echo -n "<div class=\"switchnameright\">Alle</div>"
echo "</div>"
if [ "$NOFLOAT" == "1" ]; then
  echo "<br/>"
fi
echo "</div>"

if [ "$MOBILE" != "1" -a -n "$VALID_SEND_IDS" ]; then

echo "<div style=\"float:left; border:1px solid black; margin-right:2ex; margin-bottom:2ex;\">"

ITEMCOUNT=0

for DISPID in $VALID_SEND_IDS; do
  ITEMCOUNT=$((ITEMCOUNT+1))
  NAME="$(eval echo \$DESC_$DISPID)"
  [ -z "$NAME" ] && NAME=$DISPID

  echo "<div class=\"switchbox\">"
  echo "<span class=\"alignbuttonsleft\">"
  echo " <button class=\"sendbutton\" onClick='sendButton(\"on\",\"$DISPID\");'> </button>"
  echo "</span>"
  echo "<div class=\"switchnameright\">$NAME</div>"
  echo "</div>"
  if [ "$NOFLOAT" == "1" -a $((ITEMCOUNT % 2 )) -ne 1 ]; then
    echo "<br/>"
  fi

done
echo "</div>"
fi
echo "</div>"
echo "</body>"
echo "</html>"
