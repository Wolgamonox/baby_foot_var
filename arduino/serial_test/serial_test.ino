
const int bluePin = 12;
const int redPin = 9;

int val_blue = 0;
int val_red = 0;

void setup() {
    Serial.begin(9600);
    pinMode(bluePin, INPUT);
    pinMode(redPin, INPUT);
    pinMode(LED_BUILTIN, OUTPUT);
}


void loop() {
  val_blue = digitalRead(bluePin);
  val_red = digitalRead(redPin);
  digitalWrite(LED_BUILTIN, max(val_red, val_blue));
  
  if (val_blue == HIGH){
    Serial.print('b');
  } else if (val_red == HIGH) {
    Serial.print('r');
  } else {
    Serial.print(0); 
  }
  delay(100);
}
