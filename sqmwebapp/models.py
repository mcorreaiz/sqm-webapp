import mongoengine as db
import datetime

class Usuario(db.Document):
    user_id = db.StringField(max_length=50, required=True, unique=True)
    nombre  = db.StringField(max_length=50, required=True)
    email   = db.EmailField(required=True, unique=True)

    @property
    def iniciales(self):
        splitted = self.nombre.split()
        return ('{}'*len(splitted)).format(*(i[0] for i in splitted))

class Version(db.Document):
    fsid     = db.FileField() # id de GridFS
    redactor = db.ReferenceField(Usuario)
    fecha    = db.DateTimeField(default=datetime.datetime.utcnow)
    nombre   = db.StringField(max_length=50) # Ej. R_2

class Comentario(db.Document):
    contenido = db.StringField()
    redactor  = db.ReferenceField(Usuario)
    fecha     = db.DateTimeField(default=datetime.datetime.utcnow)
    nombre    = db.StringField(max_length=50) # Ej. C_2

class Nota(db.Document):
    num                = db.StringField(max_length=5) # Ej. 25.11
    nombre             = db.StringField(max_length=50) # Ej. Contingencias tributarias
    redactores         = db.ListField(db.ReferenceField(Usuario))
    aprobadores        = db.ListField(db.ReferenceField(Usuario))
    comentadores       = db.ListField(db.ReferenceField(Usuario))
    estados_aprobacion = db.DictField() # {sigla: bool}
    ultima_version     = db.IntField()
    versiones          = db.ListField(db.ReferenceField(Version))
    ultimo_comentario  = db.IntField()
    comentarios        = db.ListField(db.ReferenceField(Comentario))
