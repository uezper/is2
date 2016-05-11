from apps.autenticacion.models import User

def load_fixtures():
    user_data = [
        
        {'username': '1',
         'password': 'pass',
         'first_name': 'Carlos Federico',
         'last_name': 'Gaona',
         'email': 'cgaona@scrunbam.com',
         'telefono': '0123 456789',
         'direccion': 'Paraguay'},
        
        {'username': '3486759',
         'password': 'pass',
         'first_name': 'Kishan',
         'last_name': 'Everild',
         'email': 'keverild@scrunbam.com',
         'telefono': '0123 456789',
         'direccion': 'South Africa'},
        
        {'username': '7452863',
         'password': 'pass',
         'first_name': 'Finnuala',
         'last_name': 'Sylvana',
         'email': 'finsyl@scrunbam.com',
         'telefono': '1594 546987',
         'direccion': 'England'},

        {'username': '741256',
         'password': 'pass',
         'first_name': 'Aaliayah',
         'last_name': 'Erja',
         'email': 'aerja@scrunbam.com',
         'telefono': '548 14588563',
         'direccion': 'India'},

        {'username': '1234865',
         'password': 'pass',
         'first_name': 'Salomon',
         'last_name': 'Mina',
         'email': 'smina@scrunbam.com',
         'telefono': '0123 4486529',
         'direccion': 'France'},

        {'username': '2718281',
         'password': 'pass',
         'first_name': 'Evike',
         'last_name': 'Severe',
         'email': 'esevere@scrunbam.com',
         'telefono': '548 17524834',
         'direccion': 'France'} 
    ]
    for user in user_data:
        u = User.users.create(**user)
        print(u)
        if u == None:
            print('Error, User.users.create(...) returned \'null\'')
        
            
