import mongoengine as db
import datetime

class Usuario(db.Document):
    user_id = db.StringField(max_length=50, required=True, unique=True)
    nombre  = db.StringField(max_length=50, required=True)
    email   = db.EmailField(required=True, unique=True)
    admin   = db.BooleanField(default=False)

    @property
    def iniciales(self):
        splitted = self.nombre.split()
        return ('{}'*len(splitted)).format(*(i[0].upper() for i in splitted))

class Comentario(db.Document):
    contenido       = db.StringField()
    redactor        = db.ReferenceField(Usuario)
    fecha           = db.DateTimeField(default=datetime.datetime.now)
    nombre          = db.StringField(max_length=50)             # Ej. C_2
    nombre_creacion = db.StringField(max_length=10)             # Ej. XX_99_99

class Version(db.Document):
    meta = {'strict': False}
    archivo         = db.FileField()                            # id de GridFS
    redactor        = db.ReferenceField(Usuario)
    fecha           = db.DateTimeField(default=datetime.datetime.now)
    comentarios     = db.ListField(db.ReferenceField(Comentario))
    nombre          = db.StringField(max_length=50)             # Ej. R_2
    nombre_creacion = db.StringField(max_length=10)             # Ej. XX_99_99

class Nota(db.Document):
    meta = {'strict': False}
    num                = db.StringField(max_length=5) # Ej. 25.11
    nombre             = db.StringField(max_length=100)             # Ej. Contingencias tributarias
    redactores         = db.ListField(db.ReferenceField(Usuario))
    fecha              = db.DateTimeField(default=datetime.datetime.now)
    aprobadores        = db.ListField(db.ReferenceField(Usuario))
    comentadores       = db.ListField(db.ReferenceField(Usuario))
    estados_aprobacion = db.DictField()                            # {user_id: bool}
    versiones          = db.ListField(db.ReferenceField(Version))
    cerrada            = db.BooleanField(default=False)

    @property
    def full_aprobado(self):
        for estado in self.estados_aprobacion.values():
            if not estado:
                return False
        return True

class Trimestre(db.Document):
    activo = db.BooleanField(default=True)
    notas  = db.ListField(db.ReferenceField(Nota))
    fecha  = db.DateTimeField(default=datetime.datetime.now)
    numero = db.IntField() # Numero de Trimestre que es

    def get_numero(trimestres, default=3): # Recibe toda la lista de trimestres
        last_trimestre = trimestres.order_by("-fecha").first()
        if last_trimestre:
            numero = last_trimestre.numero % 4 + 1
            return numero
        else:
            return default

    @property
    def nombre(self):
        return "Q{} - {}".format(self.numero, self.fecha.year)
