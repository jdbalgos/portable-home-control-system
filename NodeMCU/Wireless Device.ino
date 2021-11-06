#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <EEPROM.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define Switch1 D1
#define Switch2 D2
#define REDLED D3 
#define GREENLED D4 
#define Button2 D5
#define Button1 D6
#define BLUELED D7 


boolean lastButton1 = LOW;
boolean lastButton2 = LOW;
boolean currentButton1 = LOW;
boolean currentButton2 = LOW;

String eepromIP = "";

int web_stats = 9;

String controller_ip = "";

ESP8266WebServer server(80);

const char* ssid = "test";
const char* passphrase = "test";
String st;
String content;
int statusCode;
String Status1;
String Status2;

String DeviceID = "CTL-AA03";

void sendtoServer();
String get_ip_controller();
void changeSwitch1();

void setup() {
  pinMode(Switch2, OUTPUT);
  pinMode(Switch1, OUTPUT);
  pinMode(REDLED, OUTPUT);
  pinMode(GREENLED, OUTPUT);
  pinMode(BLUELED, OUTPUT);
  pinMode(Button1, INPUT);
  pinMode(Button2, INPUT);
  digitalWrite(REDLED, LOW);
  digitalWrite(GREENLED, LOW);
  digitalWrite(BLUELED, LOW);
  digitalWrite(Switch1, HIGH);
  digitalWrite(Switch2, HIGH);
  Serial.begin(115200);
  EEPROM.begin(512);
  delay(10);
  digitalWrite(GREENLED, HIGH);
  Serial.println();
  Serial.println();
  Serial.println("Startup");
  // read eeprom for ssid and pass
  Serial.println("Reading EEPROM ssid");
  String esid;
  for (int i = 0; i < 32; ++i)
    {
      esid += char(EEPROM.read(i));
    }
  Serial.print("SSID: ");
  Serial.println(esid);
  Serial.println("Reading EEPROM pass");
  String epass = "";
  for (int i = 32; i < 96; ++i)
    {
      epass += char(EEPROM.read(i));
    }
    Serial.print("PASS: ");
  Serial.println(epass);
    String eip_lenght= "";
   for (int i = 124; i < 126; ++i)
    {
      eip_lenght += char(EEPROM.read(i));
    }
    int eepromIP_lenght = eip_lenght.toInt();
   Serial.print("ip lenght: ");
  Serial.println(eip_lenght);
  Serial.println(eepromIP_lenght);
  for (int i = 96; i < 96+eepromIP_lenght; ++i)
    {
      eepromIP += char(EEPROM.read(i));
    }
  Serial.print("IP: ");
  Serial.println(eepromIP); 
    
  if ( esid.length() > 1 ) {
      WiFi.begin(esid.c_str(), epass.c_str());
      if (testWifi()) {
        web_stats = 0;
        launchWeb(web_stats);
        return;
      } 
  }
  setupAP();
}


bool testWifi(void) {
  int c = 0;
  Serial.println("Waiting for Wifi to connect");  
  while ( c < 35 ) {
    if (WiFi.status() == WL_CONNECTED) { digitalWrite(GREENLED, LOW); digitalWrite(BLUELED, HIGH); return true; } 
    delay(500);
    Serial.print(WiFi.status());    
    c++;
  }
  Serial.println("");
  Serial.println("Connect timed out, opening AP");
  digitalWrite(GREENLED, LOW); digitalWrite(REDLED, HIGH);
  return false;
} 

void launchWeb(int webtype) {
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("Local IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("SoftAP IP: ");
  Serial.println(WiFi.softAPIP());
  Serial.print("Webtype: ");
  Serial.println(webtype);
  if(webtype == 0){                                                 // THIS IS ONLINE
    sendtoServer(); 
    controller_ip = get_ip_controller();
    WiFi.mode(WIFI_STA);
    Serial.println("STA MODE ONLY");
    }
   else if(webtype == 1){                                                 // THIS IS ONLINE
    WiFi.softAP(DeviceID.c_str());
    WiFi.mode(WIFI_AP_STA);
    Serial.println("AP_STA MODE");
    Serial.print("DeviceID: ");
    Serial.println(DeviceID);
    }
  createWebServer(webtype);
  // Start the server
  server.begin();
  Serial.println("Server started"); 
}

void setupAP(void) {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  int n = WiFi.scanNetworks();
  Serial.println("scan done");
  if (n == 0)
    Serial.println("no networks found");
  else
  {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i)
     {
      // Print SSID and RSSI for each network found
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(")");
      Serial.println((WiFi.encryptionType(i) == ENC_TYPE_NONE)?" ":"*");
      delay(10);
     }
  }
  Serial.println(""); 
  st = "<ol>";
  for (int i = 0; i < n; ++i)
    {
      // Print SSID and RSSI for each network found
      st += "<li>";
      st += WiFi.SSID(i);
      st += " (";
      st += WiFi.RSSI(i);
      st += ")";
      st += (WiFi.encryptionType(i) == ENC_TYPE_NONE)?" ":"*";
      st += "</li>";
    }
  st += "</ol>";
  delay(100);
  WiFi.softAP(ssid, passphrase, 6);
  Serial.println("softap");
  web_stats = 1;    // not connected
  launchWeb(web_stats);
  Serial.println("over");
}

void createWebServer(int webtype)
{
  if ( webtype == 1 ) {
    /*********************************THIS IS NOT CONNECTED TO WIFI*******************************************************/
    server.on("/setting", []() {
        String qsid = server.arg("ssid");
        String qpass = server.arg("pass");
        String queip = server.arg("queip");
        String ip_lenght = server.arg("ip_len");
        if (qsid.length() > 0 && qpass.length() > 0 && queip.length() > 0 && ip_lenght.length() > 0) {
          Serial.println("clearing eeprom");
          for (int i = 0; i < 130; ++i) { EEPROM.write(i, 0); }
          Serial.println(qsid);
          Serial.println("");
          Serial.println(qpass);
          Serial.println("");
          Serial.println(queip);
          Serial.println("");
          Serial.println(ip_lenght);
          Serial.println("");
            
          Serial.println("writing eeprom ssid:");
          for (int i = 0; i < qsid.length(); ++i)
            {
              EEPROM.write(i, qsid[i]);
              Serial.print("Wrote: ");
              Serial.println(qsid[i]); 
            }
          Serial.println("writing eeprom pass:"); 
          for (int i = 0; i < qpass.length(); ++i)
            {
              EEPROM.write(32+i, qpass[i]);
              Serial.print("Wrote: ");
              Serial.println(qpass[i]); 
            }
          for (int i = 0; i < queip.length(); ++i)
            {
              EEPROM.write(96+i, queip[i]);
              Serial.print("Wrote: ");
              Serial.println(queip[i]); 
            } 
            for (int i = 0; i < ip_lenght.length(); ++i)
            {
              EEPROM.write(124+i, ip_lenght[i]);
              Serial.print("Wrote: ");
              Serial.println(ip_lenght[i]); 
            }     
          EEPROM.commit();
          content = "{\"Success\":\"saved to eeprom... reset to boot into new wifi\"}";
          statusCode = 200;
          server.send(statusCode, "application/json", content);
          while(1){
          digitalWrite(REDLED, LOW);
          digitalWrite(GREENLED, LOW);
          digitalWrite(BLUELED, LOW);
          digitalWrite(REDLED, HIGH);
          delay(500);
          digitalWrite(REDLED, LOW);
          delay(500);
          digitalWrite(GREENLED, HIGH);
          delay(500);
          digitalWrite(GREENLED, LOW);
          delay(500);
          digitalWrite(BLUELED, HIGH);
          delay(500);
          digitalWrite(BLUELED, LOW);
          delay(500);
          }
        } else {
          content = "{\"Error\":\"404 not found\"}";
          statusCode = 404;
          Serial.println("Sending 404");
          server.send(statusCode, "application/json", content);
        }
        
    });
  } else if (webtype == 0) {

    /*********************************THIS IS CONNECTED TO WIFI*******************************************************/
    server.on("/", []() {
      if(digitalRead(Switch1)) Status1 = "OFF"; else Status1 = "ON";
      if(digitalRead(Switch2)) Status2 = "OFF"; else Status2 = "ON";
      IPAddress ip = WiFi.localIP();
      String ipStr = String(ip[0]) + '.' + String(ip[1]) + '.' + String(ip[2]) + '.' + String(ip[3]);
      //server.send(200, "application/json", "{\"IP\":\"" + ipStr + "\"}");
      server.send(200, "application/json", "{\"Switch1\":\"" + Status1 + "\",\"Switch2\":\"" + Status2 + "\",\"Device\":\"" + DeviceID + "\",\"IP\":\"" + ipStr + "\"}");
    });
    server.on("/cleareeprom", []() {
      content = "<!DOCTYPE HTML>\r\n<html>";
      content += "<p>Clearing the EEPROM</p></html>";
      server.send(200, "text/html", content);
      Serial.println("clearing eeprom");
      for (int i = 0; i < 120; ++i) { EEPROM.write(i, 0); }
      EEPROM.commit();
    });
    server.on("/query", []() {
      String qStatus1 = server.arg("Switch1");
      String qStatus2 = server.arg("Switch2");
      server.send(200, "text/html", content);
      Serial.println("Switch1:" + qStatus1);
      Serial.println("Switch2:" + qStatus2);
      if(qStatus1 == "true"){
        digitalWrite(D1, LOW);
        for(int x=0; x<= 3; x++){
          digitalWrite(BLUELED, LOW);
          delay(200);
          digitalWrite(BLUELED, HIGH);
          delay(200);
        }
      } 
      else if(qStatus1 == "false") {
        digitalWrite(D1, HIGH);
        for(int x=0; x<= 3; x++){
          digitalWrite(BLUELED, LOW);
          delay(200);
          digitalWrite(BLUELED, HIGH);
          delay(200);
        }
      }
      if(qStatus2 == "true") {
        digitalWrite(D2, LOW); 
        for(int x=0; x<= 3; x++){
          digitalWrite(BLUELED, LOW);
          delay(200);
          digitalWrite(BLUELED, HIGH);
          delay(200);
        }
      }
      else if(qStatus2 == "false") {
        digitalWrite(D2, HIGH);
        for(int x=0; x<= 3; x++){
          digitalWrite(BLUELED, LOW);
          delay(200);
          digitalWrite(BLUELED, HIGH);
          delay(200);
        }
      }
    });
    server.on("/setting", []() {
        String qsid = server.arg("ssid");
        String qpass = server.arg("pass");
        String queip = server.arg("queip");
        String ip_lenght = server.arg("ip_len");
        if (qsid.length() > 0 && qpass.length() > 0 && queip.length() > 0 && ip_lenght.length() > 0) {
          Serial.println("clearing eeprom");
          for (int i = 0; i < 130; ++i) { EEPROM.write(i, 0); }
          Serial.println(qsid);
          Serial.println("");
          Serial.println(qpass);
          Serial.println("");
          Serial.println(queip);
          Serial.println("");
          Serial.println(ip_lenght);
          Serial.println("");
            
          Serial.println("writing eeprom ssid:");
          for (int i = 0; i < qsid.length(); ++i)
            {
              EEPROM.write(i, qsid[i]);
              Serial.print("Wrote: ");
              Serial.println(qsid[i]); 
            }
          Serial.println("writing eeprom pass:"); 
          for (int i = 0; i < qpass.length(); ++i)
            {
              EEPROM.write(32+i, qpass[i]);
              Serial.print("Wrote: ");
              Serial.println(qpass[i]); 
            }
          for (int i = 0; i < queip.length(); ++i)
            {
              EEPROM.write(96+i, queip[i]);
              Serial.print("Wrote: ");
              Serial.println(queip[i]); 
            } 
            for (int i = 0; i < ip_lenght.length(); ++i)
            {
              EEPROM.write(124+i, ip_lenght[i]);
              Serial.print("Wrote: ");
              Serial.println(ip_lenght[i]); 
            } 
          EEPROM.commit();
          content = "{\"Success\":\"saved to eeprom... reset to boot into new wifi\"}";
          statusCode = 200;
          server.send(statusCode, "application/json", content);
          while(1){
          digitalWrite(REDLED, LOW);
          digitalWrite(GREENLED, LOW);
          digitalWrite(BLUELED, LOW);
          digitalWrite(REDLED, HIGH);
          delay(500);
          digitalWrite(REDLED, LOW);
          delay(500);
          digitalWrite(GREENLED, HIGH);
          delay(500);
          digitalWrite(GREENLED, LOW);
          delay(500);
          digitalWrite(BLUELED, HIGH);
          delay(500);
          digitalWrite(BLUELED, LOW);
          delay(500);
          }
          
        } else {
          content = "{\"Error\":\"404 not found\"}";
          statusCode = 404;
          Serial.println("Sending 404");
          server.send(statusCode, "application/json", content);
        }    
    });
  }
}

void loop() { /*****************************************************************************************/
  server.handleClient();
  if(digitalRead(Button1) == 1) changeSwitch1();
  if(digitalRead(Button2) == 1) changeSwitch2();
}


void sendtoServer() {
      IPAddress ip = WiFi.localIP();
      digitalWrite(D1, HIGH);
      digitalWrite(D2, HIGH);
      String ipStr = String(ip[0]) + '.' + String(ip[1]) + '.' + String(ip[2]) + '.' + String(ip[3]);
      //server.send(200, "application/json", "{\"IP\":\"" + ipStr + "\"}");
      StaticJsonBuffer<300> JSONbuffer;
      JsonObject& JSONencoder = JSONbuffer.createObject();
      JSONencoder["ip_address"] = ipStr;
      JSONencoder["device_name"] = DeviceID;
      char JSONmessageBuffer[300];
      JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
      Serial.println(JSONmessageBuffer);
      HTTPClient http;
      String query= "http://" + eepromIP;
      query = query + "/sendmyip";
      Serial.println(query);
      http.begin(query);
      http.addHeader("Content-Type", "application/json");
      int httpCode = http.POST(JSONmessageBuffer); //Send the request
      String payload = http.getString(); //Get the response payload
      Serial.println(httpCode); //Print HTTP return code
      Serial.println(payload); //Print request response payload
      http.end(); //Close connection
}

String get_ip_controller(){
    HTTPClient http;  //Declare an object of class HTTPClient
    String query = "http://"+ eepromIP;
    query = query + "/getipcontroller";
    Serial.println(query);
    http.begin(query);  //Specify request destination
    int httpCode = http.GET();                                                                  //Send the request
    if (httpCode > 0) { //Check the returning code
      String payload = http.getString();   //Get the request response payload
      Serial.println(payload);
      return payload;
      }

}



void changeSwitch1(){
  Serial.println("Push Button1 pushed");
  Serial.print("Reading Switch1 Status");
  Serial.println(digitalRead(Switch1));
  boolean memoryButton = digitalRead(Switch1);
  boolean newMemory = !memoryButton;
  digitalWrite(Switch1, newMemory);
  Serial.println(controller_ip);
  Serial.print("WebStats: ");
  Serial.println(web_stats);
  if(web_stats == 0){
    //update_send_to_server("1", newMemory);
  }

  delay(1000);
}

void changeSwitch2(){
  Serial.println("Push Button2 pushed");
  Serial.print("Reading Switch2 Status");
  Serial.println(digitalRead(Switch2));
  boolean memoryButton = digitalRead(Switch2);
  boolean newMemory = !memoryButton;
  digitalWrite(Switch2, newMemory);
  Serial.println(controller_ip);
  Serial.print("WebStats: ");
  Serial.println(web_stats);
  if(web_stats == 0){
   //update_send_to_server("2", newMemory);
  }
  delay(1000);
}


void update_send_to_server(String switch_position, boolean switch_status){
  Serial.print("Switch position: ");
  Serial.println(switch_position);
  Serial.print("Switch Status: ");
  Serial.println(switch_status);
  StaticJsonBuffer<300> JSONbuffer;
  JsonObject& JSONencoder = JSONbuffer.createObject();
  JSONencoder["switch_position"] = switch_position;
  JSONencoder["device_name"] = DeviceID;
  JSONencoder["switch_status"] = switch_status;
  char JSONmessageBuffer[300];
  JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  Serial.println(JSONmessageBuffer);
  HTTPClient http;
  http.begin("http://" + eepromIP +"/switchhttp");
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(JSONmessageBuffer); //Send the request
  String payload = http.getString(); //Get the response payload
  Serial.println(httpCode); //Print HTTP return code
  Serial.println(payload); //Print request response payload
  http.end(); //Close connection
}



