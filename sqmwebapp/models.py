import mongoengine as db
import datetime

class Usuario(db.Document):
    user_id = db.StringField(max_length=50, required=True, unique=True)
    nombre  = db.StringField(max_length=50, required=True)
    email   = db.EmailField(required=True, unique=True)

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
    num                = db.StringField(max_length=5, unique=True) # Ej. 25.11
    nombre             = db.StringField(max_length=50)             # Ej. Contingencias tributarias
    redactores         = db.ListField(db.ReferenceField(Usuario))
    aprobadores        = db.ListField(db.ReferenceField(Usuario))
    comentadores       = db.ListField(db.ReferenceField(Usuario))
    estados_aprobacion = db.DictField()                            # {user_id: bool}
    versiones          = db.ListField(db.ReferenceField(Version))

    @property
    def full_aprobado(self):
        for estado in self.estados_aprobacion.values():
            if not estado:
                return False
        return True
