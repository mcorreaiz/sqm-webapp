from . import db

class Usuario(db.Document):
    nombre = db.StringField(max_length=50)
    sigla  = db.StringField(max_length=2)
    token  = db.StringField(max_length=50)
    email  = db.EmailField()

class Version(db.EmbeddedDocument):
    fsid     = db.IntField() # id de GridFS
    redactor = db.ReferenceField(Usuario)
    fecha    = db.DateTimeField()

class Comentario(db.EmbeddedDocument):
    contenido = db.StringField()
    redactor  = db.ReferenceField(Usuario)
    fecha     = db.DateTimeField()

class Nota(db.Document):
    num                = db.StringField(max_length=5) # Ej. 25.11
    nombre             = db.StringField(max_length=50) # Ej. Contingencias tributarias
    redactores         = db.ListField(db.ReferenceField(Usuario))
    aprobadores        = db.ListField(db.ReferenceField(Usuario))
    comentadores       = db.ListField(db.ReferenceField(Usuario))
    estados_aprobacion = db.DictField() # {sigla: bool}
    ultima_version     = db.IntField()
    versiones          = db.ListField(db.EmbeddedDocumentField(Version))
    ultimo_comentario  = db.IntField()
    comentarios        = db.ListField(db.EmbeddedDocumentField(Comentario))
