#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <ESP32Servo.h>

// Definición de pines y configuración del DHT y el servo motor
#define BOMA_PIN 17         // Pin de la bomba de agua
#define DHTPIN 15           // Pin de datos del sensor DHT
#define DHTTYPE DHT11       // Cambiar a DHT22 si usas ese sensor
#define SERVO_PIN 18        // Pin del servo motor
DHT dht(DHTPIN, DHTTYPE);
Servo myServo;

// Pines de los sensores LM35 en el ESP32
int sensor1 = 33;  // Primer sensor en GPIO33
int sensor2 = 35;  // Segundo sensor en GPIO35
int sensor3 = 32;  // Tercer sensor en GPIO32

// Pin PWM donde está conectado el ventilador
const int ventiladorPin = 21;

// Número de lecturas para promediar
const int numLecturas = 10;

void setup() {
  // Configuración inicial
  Serial.begin(115200);
  pinMode(BOMA_PIN, OUTPUT);  // Configura el pin de la bomba como salida
  digitalWrite(BOMA_PIN, LOW);  // Apaga la bomba inicialmente
  dht.begin();  // Inicializa el sensor DHT
  myServo.attach(SERVO_PIN);  // Conecta el servo

  // Configuración del pin del ventilador como salida
  pinMode(ventiladorPin, OUTPUT);
  Serial.println("Sistema iniciado. Esperando comandos...");
}

void loop() {
  // Procesamiento de comandos seriales
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');  // Lee el comando hasta un salto de línea

    // Comandos para la bomba
    if (comando == "ON") {
      digitalWrite(BOMA_PIN, HIGH);  // Enciende la bomba
      Serial.println("Bomba encendida");
    } 
    else if (comando == "OFF") {
      digitalWrite(BOMA_PIN, LOW);   // Apaga la bomba
      Serial.println("Bomba apagada");
    }
    
    // Comandos para el servo
    else if (comando == "SERVO_A") {
      myServo.write(90);  // Mueve el servo a 90 grados
      Serial.println("Servo a 90 grados");
    }
    else if (comando == "SERVO_B") {
      myServo.write(0);   // Mueve el servo a 0 grados
      Serial.println("Servo a 0 grados");
    }

    // Comando para leer el sensor DHT
    else if (comando == "READ_SENSOR") {
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();

      if (isnan(humidity) || isnan(temperature)) {
        Serial.println("Error al leer el sensor DHT11!");
      } else {
        Serial.print("HUMEDAD:");
        Serial.print(humidity);
        Serial.print(" ");
        Serial.print("TEMP:");
        Serial.println(temperature);
      }
    }
  }

  // Leer cada sensor LM35 y calcular el promedio de las lecturas
  float temp1 = leerTemperaturaPromedio(sensor1);
  float temp2 = leerTemperaturaPromedio(sensor2);
  float temp3 = leerTemperaturaPromedio(sensor3);

  // Calcular el promedio de las tres temperaturas
  float promedio = (temp1 + temp2 + temp3) / 3.0;

  // Control del ventilador según el promedio de temperatura
  if (promedio >= 30.0) {
    analogWrite(ventiladorPin, 255); // Máxima velocidad
  } else if (promedio < 20.0) {
    analogWrite(ventiladorPin, 25); // Velocidad reducida
  }

  // Mover el servo motor según el promedio de temperatura
  if (promedio >= 30.0) {
    myServo.write(90);  // Gira a 90 grados a favor de las manecillas del reloj
  } else if (promedio < 19.0) {
    myServo.write(-90); // Gira -90 grados (en contra de las manecillas del reloj)
  }

  // Imprimir las temperaturas y el promedio en el monitor serial
  Serial.print("Temperatura 1: ");
  Serial.print(temp1);
  Serial.println(" °C");

  Serial.print("Temperatura 2: ");
  Serial.print(temp2);
  Serial.println(" °C");

  Serial.print("Temperatura 3: ");
  Serial.print(temp3);
  Serial.println(" °C");

  Serial.print("Promedio de temperatura: ");
  Serial.print(promedio);
  Serial.println(" °C");

  delay(1000);  // Esperar 1 segundo antes de tomar una nueva lectura
}

// Función que convierte la lectura analógica a temperatura en grados Celsius,
// con promediado para mejorar la precisión
float leerTemperaturaPromedio(int pin) {
  float suma = 0;

  // Realiza varias lecturas y acumula el resultado
  for (int i = 0; i < numLecturas; i++) {
    int lectura = analogRead(pin);             // Lee el pin analógico
    float voltaje = lectura * (3.3 / 4095.0);  // Convierte la lectura en voltaje (3.3V en lugar de 5V)
    float temperatura = voltaje * 100;         // Convierte el voltaje a grados Celsius
    suma += temperatura;
    delay(10);  // Espera un corto tiempo entre lecturas para evitar ruido
  }

  // Calcula el promedio de las lecturas
  return suma / numLecturas;
}