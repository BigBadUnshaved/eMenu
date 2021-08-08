# eMenu

Rozwiązanie zadania rekrutacyjnego dla www.cloudservices.pl z wymaganiami na końcu tego pliku.
Aplikacja ta stanowi prototyp serwisu służacego jako restauracyjna karta menu online.
Na branchu main znajduje się rozwiązanie oddane w terminie, branch 1.1 oraz 1.1-develop zawierają
dalsze prace w celu poprawy błędów (funkcjonalnych i stylistycznych)

Instrukcja Instalacji:

Po sklonowaniu repozytorium, aby zapewnić prawidłowe działanie aplikacji należy uruchomić ją korzystając 
z dostarczonego docker-compose.yml znajdującego się w katalogu głównym projektu. W czasie pracy
i testowania projektu wykorzystano wersje Docker==20.10.7 oraz docker-compose==1.27.4

W celu uniknięcia problemów, sugeruje się uruchomienie aplikacji korzystając z Linuxa - projekt nie był
testowany z innymi systemami operacyjnymi (prace i testy wykonano w Linux Mint 19)
Dodatkowo, aby narzędzie raportowania wysyłało faktyczne emaile, należy prawidłowo skonfigurować
ustawienia skrzynki mailowej i wybrać odpowiedni backend.


Dokumentacja

Po uruchomieniu aplikacji swagger wygeneruje dokumentację, którą będzie można znaleźć pod adresem
{$HOST}/swagger-ui/ (domyślnie http://127.0.0.1:8000/swagger-ui/, w przypadku innej konfiguracji
dokumentacja może znajdować się pod innym adresem)


Krótko o przestrzeni nazw url projektu

/admin/      - panel django admin; w czasie inicjalizacji projektu nie wygenerowano admina
               (zainteresowani będą musieli skorzystać z opcji python manage.py createsuperuser)
               
/api/        - widoki wygenerowane przy użyciu django rest framework i podstawa serwisu

/card/       - widoki powstałe przy użyciu django.views.generic, używane do renderowania wersji serwisu
               przystępniejszej dla przeciętnego użytkownika; ostrzeżenie: działanie i nazwy części parametrów 
               get użytych do filtrowania listy kart menu (obiekt Card) różni się od tych użytych w wersji /api/.
               Użyto gotowego wzorca css ramayana wykonanego przez Template Mo.
               
/swagger-ui/ - dokumentacja wygenerowana przez swagger'a; z powodu konfliktów jakie pyyaml potrafi spowodować
               gdy się w modelach korzysta z DecimalField, automatycznie generowany plik schemy generował
               błąd (dokładniej to dodanie minimalnej wielkości ceny (Dish.price) dodawał tag, który
               zakłócał działanie swagger'a; z tego powodu plik wygenerowano plik schemy, który następnie
               przekonwertowano na format json i przechowano w folderze /static/
               
               


Treść zadania:

Zadanie Python (dowolny framework i narządzia):
Projekt i implementacja samodzielnego serwisu eMenu, służącego jako restauracyjna karta menu
online.


Wymagania stawiane aplikacji:
API niepublicznie:

1. REST API do zarządzania menu
2. Możliwość tworzenia wielu wersji kart (menu) o unikalnej nazwie.
3. Każda karta może zawierać dowolną liczbę dań.
4. Każde danie powinno charakteryzować się: nazwą, opisem, ceną, czasem przygotowania, datą
   dodania, datą aktualizacji, informacją czy danie jest wegetariańskie
5. Każda karta charakteryzuje się: nazwą (unikalna), opisem, datą dodania, datą aktualizacji
6. API musi być zabezpieczone przed nieautoryzowanym dostępem (po autoryzacji użytkownika)

API publicznie:
1. Rest API do przeglądania niepustych karta menu.
2. Możliwość sortowanie listy po nazwie oraz liczbie dań, za pomocą parametrów GET
3. Filtrowanie listy po nazwie oraz okresie dodanie i ostatnie aktualizacji
4. Detal karty prezentujący wszystkie dana dotyczące karty oraz dań w karcie.

Raportowanie:
1. Przygotować mechanizm, który raz dziennie o 10:00 wyśle e-mail do wszystkich użytkowników
aplikacji
2. E-mail musi zawierać informację o nowa dodanych przepisach oraz ostatnio
zmodyfikowanych przepisach
3. Wysyłamy informację tylko o tych, który zostały zmodyfikowane poprzedniego dnia.

Dodatkowo:
1. Konieczne jest załączenie instrukcji instalacji oraz uruchomienia projektu
2. Mile widziane jest przygotowanie aplikacji po uruchomienie w Docker (Dockerfile oraz
docker-compose.yml do uruchomienia aplikacji)
3. Dopuszczalne jest korzystanie z ogólnodostępnych rozwiązań.
4. Dane inicjalizacyjne do projektu są mile widziane.
5. Konieczne jest udokumentowane API za pomocą Swagger lub innego narzędzia
(dokumentacja powinna być generowana automatycznie)
6. Możliwość dodania zdjęcia dania nie jest wymagana, lecz jej obecność zostanie pozytywnie
odebrana.
7. Sposób dostarczenia aplikacji jest dowolny, jednak w miarę możliwości zachęcamy do
skorzystania z GitHub-a.
8. Dostarczony kod powinien posiadać pokrycie testami na poziomie min. 70% (coverage),
dotyczy wyłącznie kodu napisanego przez kandydata (bez uwzględniania testów
zewnętrznych bibliotek).9. Należy pamiętać o odpowiednich ustawieniach lokalizacyjnych oraz problemach związanych z
optymalizacją liczby zapytań do bazy danych.
10. Koniecznym jest wykorzystanie relacyjnego silnika bazodanowego (możliwe do uruchomienia
na PostgreSQL bez ingerencji w kod, prócz konfiguracji)

Oceniane będą:
1. wykorzystanie i znajomość języka Python
2. wykorzystanie i znajomość wybranego Frameworka,
3. wykorzystanie i znajomość dobrych praktyk pisania kodu
4. wykorzystanie i znajomość wzorców projektowych
5. wykorzystanie i znajomość standardów REST API
6. wykorzystanie i znajomość systemu kontroli wersji GIT
