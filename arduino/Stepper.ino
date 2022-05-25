// Define pin connections & motor's steps per revolution
const unsigned char dirPin = 9;
const unsigned char stepPin = 8;
const unsigned char slp_rst_vddPin = 7;
const unsigned char stepsPerRevolution = 200; // The stepper motor we have makes 1.8 degree per step, so, we need 200 steps to make a 360 degree revolution
unsigned char enFlag = 0;

void setup()
{
  // Declare pins as Outputs
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(slp_rst_vddPin, OUTPUT);
  Serial.begin(9600);
  
}
void loop()
{

  // Stepper motor never revolutes until we enable flag becomes 1
  if (enFlag == 1) {
    // Sleep & reset pins are active low
    // So we set sleep, reset pins to high to disable them
    // We also set vdd pin to high to feed the driver
    digitalWrite(slp_rst_vddPin, HIGH);
    
    // Set motor direction clockwise
    digitalWrite(dirPin, HIGH);

    // Step pin is responsible for pulses
    // So we give it high for 2000 microseconds and give it back low to make a pulse
    // 1 pulse = 1 step
    // 200 steps = 360 degree revolution
    for (int i = 0; i < stepsPerRevolution; i++)
    {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(2000);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(2000);
    }
  }

    // Wait until taking read from serial monitor
    while (!Serial.available());
    enFlag = Serial.readString().toInt();


}
