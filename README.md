# openBCI-project-embedded-web

Om ons project te laten runnen moet u MongoDB installeren. 
Dat kan u doen op deze link: https://www.mongodb.com/try/download/community. Hier moet u de community server versie installeren. Dit is de MongoDB service.
Wanneer de installer u vraagt of u DBCompass ook wilt installeren, doe dit zeker.

U kan ofwel de database invullen met data uit een openBCI helm, ofwel kan u verder gaan met een vooraf ingevulde database.

Als u zelf de database wilt invullen met data uit de helm, moet u de 'Helmet data Extraction' scripts uitvoeren op een apparaat die verbinding kan maken met de helm.
Hiervoor moet de openBCI helm aanstaan en de bluetooth dongle in het apparaat steken.
In deze scripts moet u misschien nog het ip address aanpassen van het toestel waar de restful/RabbitMQ server op draait.
De virtual environments waar u deze scripts mee moet runnen zitten in de bijbehorende venv map. Hier moet python.exe worden gebruikt als interpreter.

Deze servers zijn aanwezig in de folder 'Server'. Deze kan u runnen in een terminal met node.
Om de restful server te draaien moet je de 'express' module installeren met het commando 'npm install express'.
Om de RabbitMQ server te draaien moet je aqmplib installeren met het commando 'npm install aqmplib'. 
De RabbitMQ server is niet getest in combinatie met de helm, enkel met gesimuleerde data injectie gedraait op de computer waar de server op draait.

Om zelf de database te vullen met vooraf verkregen data, kan u 'testCollection.json' gebruiken, zo kan u de rest van het project uitproberen.
Hiervoor moet u eerst MongoDB Compass openen. Dan moet u connecteren met de MongoDB service door in mongoDBcompass te connecteren met: 'mongodb://localhost:27017/'.
Dan om de collectie te importeren, moet u een nieuwe database en collectie creëren. Daarna kan u vanboven naar 'Collection' gaan, en op 'import data' klikken. 
Dit gaat de huidige collectie vullen met data uit een bestand, we gaan het jsonbestand 'testCollection.json' gebruiken hiervoor.

Als de database gevuld is en de restful API server draaiend is, kan u de visualization client runnen en de data uit de database visualiseren.
De python virtual environment voor deze visualization client bevind zich ook in de venv folder, de python exe hier moet u instellen als interpreter voor deze python script.
