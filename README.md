# Rapport Service
Rapport Service er en mikroservice designet til at hjælpe forretningsudviklere med at samle data fra to andre mikroservices - Lejeaftale Service og Skades Service - for at generere rapporter og analysere data. Servicen anvender JWT til autentifikation og indeholder flere endpoints til at hente og manipulere data.


## Indholdsfortegnelse

1. [Funktioner](#funktioner)
2. [Arkitektur](#arkitektur)
3. [Forudsætninger](#forudsætninger)
4. [Opsætning og installation](#opsætning-og-installation)
5. [Filstruktur](#filstruktur)
6. [General information](#general-information)
7. [JWT Autentificering](#JWT-autentificering)
8. [Endpoints:](#endpoints)
    1. [Login](#login)
    2. [Beskyttet endpoint](#beskyttet-endpoint)
    3. [Hent lejeaftaler](#hent-lejeaftaler)
    4. [Eksporter skades data som CSV](#eksporter-skades-data-som-CSV)
    5. [Flere endpoints](#flere-endpoints)
9. [Testing](#testing)
10. [Kontakt](#kontakt)


## Funktionalitet

**Servicen har følgende funktioner**:

1. Autentificering med JWT: Login og adgang til beskyttede ressourcer via JSON Web Tokens.
2. Dataindsamling fra Lejeaftale Service:
  * Hent data om lejede biler og beregn den samlede pris.
  * Gem data om lejede biler i en lokal SQLite-database.
3. Dataindsamling fra Skades Service:
  * Hent data om beskadigede biler og beregn økonomiske tab baseret på skadeniveau.
4. CSV-eksport:
  * Eksporter data om beskadigede biler og tab i CSV-format.

---

## Arkitektur
Rapport Service er en RESTful microservice, bygget med Flask og er integreret med en SQLite-database. Den følger en modulær struktur, hvor funktioner og ansvar er opdelt i forskellige services og filer.

**Overblik over arkitekturen**:

* API Gateway: Rapport Service fungerer som en hoved gateway til at hente og manipulere data fra både Lejeaftale Service og Skades Service.
* Autentifikation: JWT (JSON Web Tokens) bruges til at autentificere og autorisere brugere.
* Database: En lokal SQLite-database bruges til at gemme den producerede rapportdata.
* Datahåndtering: Rapport Service bruger HTTP-forespørgsler til at hente data fra andre mikroservices.

**Flow**:

1. Bruger logger ind og modtager en JWT-token.
2. Rapport Service kommunikerer med Lejeaftale Service og Skades Service for at hente data.
3. Data kombineres og præsenteres til brugeren eller gemmes i databasen som en rapport.

---

## Filarkitektur
```bash
/Projekt
│
├── app.py                  # Hovedapplikationen og API-ruter
├── Dockerfile              # Docker-konfiguration til containerisering
├── Database/
│   ├── rapport.db          # SQLite-database
│   └── user.py             # Brugerdatabase
├── Services/
│   ├── auth.py             # Håndtering af autentifikation
│   ├── cars.py             # Håndtering af lejeaftale-data
│   ├── damages.py          # Håndtering af skadesdata
│   ├── generateCSV.py      # Generering af CSV-rapporter
├── swagger/
│   ├── config.py           # Swagger-konfiguration til API-dokumentation
│   └── *.yaml              # Swagger-filer til endpoints
└── .env                    # Miljøvariabler (f.eks. API-nøgler)
```

---

## Forudsætninger
- Python 3.8 eller højere
- Flask 2.x
- SQLite til databasen
- Swagger UI eller Postman til API-testning

---

## Opsætning og installation

1. **Klon repository**:
   ```bash
   git clone https://github.com/yourusername/RapportService.git
   cd RapportService

2. **Opret og aktiver virtuelt minljø**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate # på macOS/Linux
   
3. **Installer dependencies**: Brug pip til at installere de nødvendige libraries.
   ```bash 
   pip install -r requirements.txt

4. **Opsæt databasen**: Kør dette script for at initialisere SQLite-databasen:
   ```bash
   python setup_database.py

5. **Kør servicen**: Start Flask serveren.
   ```bash
   python app.py

6. **Få adgang til tjenesten**: Nu køre microservicen på:
   ```bash
   http://localhost:5002

---

## Generel information

* Base URL: `http://localhost:5001/
* Autentifikation: De fleste endpoints kræver en JWT-token, som kan fås ved at logge ind med `/login`.
* Format: Alt data sendes og modtages i JSON-format.
* Swagger Dokumentation: Endpoints er dokumenteret med Swagger og kan findes på `/swagger`.

---

## JWT Autentificering
Servicen bruger JWT (JSON Web Tokens) til autentificering og sikker benyttelse af beskyttede endpoints.

### Hvad er en JWT?
En JWT er en kompakt, sikker token, som bruges til at autentificere og autorisere brugere. Den indeholder brugerens identitet og andre oplysninger i et krypteret format, som kan verificeres uden en server-side session.

### Sådan fungerer det i Rapport Service:
* Når en bruger logger ind via `/login`, genereres et JWT-token og gemmes som en cookie (`access_token).
* Efter login bliver JWT-tokenet brugt til at få adgang til beskyttede endpoints.

### Sådan får du en JWT-token:
Brug `/login` endpointet med følgende JSON-payload:

```json
POST /login
{
  "email": "test@test.com",
  "password": "password123"
}
```
Hvis login lykkes, vil JWT-tokenet blive gemt i cookies.

### Adgang til beskyttede endpoints:
* Når du har et gyldigt JWT-token i dine cookies, vil det automatisk blive sendt med anmodninger til beskyttede endpoints.
* Eksempel:
  * `/protected` - Få adgang til information om den aktuelle bruger.
  * `/process-skade-niveau/<int:damage_niveau>` - Hent data relateret til beskradiget biler og forretnings omkostninger. (virker måde med eller uden `/<int:damage_niveau>` parameteret)

---

## Database
Servicen bruger en SQLite-database til at gemme rapport data. Databasen kan findes under `Database/rapport.db` og indeholder følgende tabel:

Rapport databasen:

| Kolonne                |	Beskrivelse                       |
|------------------------|------------------------------------|
| `Antal_Udlejede_Biler` | Antallet af lejede biler.          |
| `RapportDato`	         | Dato for oprettelse af rapporten.  |
| `Sammenlagt_Pris`	     | Samlet pris for lejede biler.      |



## Brug af Docker
Servicen kan også køre som en Docker-container:

1. Byg Docker-billedet:
```bash
docker build -t rapport-service .
```
Kør Docker-containeren:
```bash
docker run -p 5001:5001 rapport-service
```

---

## Endpoints

## 1. Login
URL: `/login`
Metode: POST
Beskrivelse: Autentificer bruger og returner en JWT-token.

**Request**:

```json
{
    "email": "test@test.com",
    "password": "password123"
}
```
**Response (200 OK)**:

```json
{
    "msg": "Login successful",
    "user": "test@test.com",
    "access_token": "<JWT-token>"
}
```


## 2. Beskyttet endpoint
URL: `/protected`
Metode: GET
Beskrivelse: Kræver autentificering. Returnerer oplysninger om den loggede bruger.

**Header**:
Authorization: Bearer <JWT-token>

**Response (200 OK)**:

```json
{
    "logged_in_as": "test@test.com",
    "msg": "You have access to this resource"
}
```

## 3. Hent lejeaftaler
URL: `/udlejedeBiler`
Metode: GET
Beskrivelse: Hent en liste af udlejede biler og den samlede pris.

**Response (200 OK)**:

```json

{
    "rented_cars": [
        {
            "bil_id": 1,
            "kunde_id": 2,
            "total_price": 3000
        }
    ],
    "total_price_sum": 3000
}
```


## 4. Eksporter skades data som CSV
URL: `/export-skadet-biler`
Metode: GET
Beskrivelse: Eksporter data over skadede biler som en CSV-fil.

**Response: En CSV-fil med følgende struktur**:

```yaml
BilID, SkadeNiveau, Loss
1, 2, 6000
2, 3, 9000
```


### Flere endpoints

Andre endpoints inkluderer:

* `/process-skade-niveau/<int:damage_niveau>` (Hent skade-data baseret på skade-niveau)
* `/gemUdlejedeBiler` (Gemmer udlejede biler i databasen)

Se Swagger-dokumentationen for en komplet liste over endpoints.

---

## Testing
Testning kan udføres med Postman eller lignende værktøjer til API-test. Følg disse trin for at teste:

1. Start applikationen ved at køre:

```bash
python app.py
```

2. Log ind via /login og få en JWT-token.
* Indtast en bruger, ved at kopiere bruger oplysninger fra `Database/user.py`.

3. Brug JWT-tokenen til at tilgå beskyttede endpoints som `/protected.

### Integrationstests
* Sørg for at have Lejeaftale Service og Skades Service kørende på deres respektive porte (`5003` og `5002`).
* Test at et endpoints som `/udlejedeBiler` og `/process-skade-niveau` henter og behandler data fra de eksterne microservices korrekt.

---

## Swagger Dokumentation
Swagger-dokumentation er tilgængelig for alle endpoints. Når servicen kører kan man få adgang til Swagger UI på:
`http://localhost:5001/apidocs`

---

### Kontakt

Hvis du har nogen spørgsmål eller oplever problemer, så er du velkommen til at kontakt udviklerteamet: Natazja, Sofie og Viktor.
