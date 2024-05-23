from functools import wraps
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_restful import Api, Resource
from flask_migrate import Migrate
import pymysql

#config
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:bola2020@85.239.239.196/usuarios'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "aplicacao_flask"
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
migrate = Migrate(app, db)


#entidade
class Usuario():
    def __init__(self, nome, email, senha, is_admin):
        self.__nome = nome
        self.__email = email
        self.__senha = senha
        self.__is_admin = is_admin
    
    @property
    def nome(self):
        return self.__nome
    
    @nome.setter 
    def nome(self, nome):
        self.__nome = nome

    @property
    def email(self):
        return self.__email
    
    @email.setter 
    def email(self, email):
        self.__email = email

    @property
    def senha(self):
        return self.__senha
    
    @senha.setter 
    def senha(self, senha):
        self.__senha = senha

    @property
    def is_admin(self):
        return self.__is_admin
    
    @is_admin.setter 
    def is_admin(self, is_admin):
        self.__is_admin = is_admin


#model
class UsuarioModel(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean)


#Schema
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UsuarioModel()
        load_instance = True
        fields = ('id', 'nome', 'email', 'senha', 'is_admin')

    nome = fields.String(required=True)
    email = fields.String(required=True)
    senha = fields.String(required=True)
    is_admin = fields.Boolean(required=True)


#service
def cadastro_usuarios(usuario):
    usuario_db = UsuarioModel(nome=usuario.nome, email=usuario.email, senha=usuario.senha, is_admin=usuario.is_admin)
    db.session.add(usuario_db)
    db.session.commit()
    return usuario_db

def listar_tudo():
    usuario_db = UsuarioModel.query.all()
    return usuario_db

def listar_por_id(id):
    usuario_db = UsuarioModel.query.filter_by(id=id).first()
    return usuario_db

def atualizar_dados(usuario_antigo, usuario_novo):
    usuario_antigo.nome = usuario_novo.nome
    usuario_antigo.email = usuario_novo.email
    usuario_antigo.senha = usuario_novo.senha
    usuario_antigo.is_admin = usuario_novo.is_admin
    db.session.commit()

def deletar_usuario(id):
    db.session.delete(id)
    db.session.commit()

def listar_usuario_email(email):
    return UsuarioModel.Usuario.query.filter_by(email=email).first()

def listar_usuario_id(id):
    return UsuarioModel.Usuario.query.filter_by(id=id).first()



#Views
class UsuarioList(Resource):

    def get(self):
        us = UsuarioSchema(many=True)
        x = listar_tudo()
        resultado = us.jsonify(x)

        return make_response(resultado, 200)

    def post(self):
        us = UsuarioSchema()
        validate = us.validate(request.json)
        if validate:
            return make_response(jsonify(validate), 400)
        else:
            nome = request.json["nome"]
            email = request.json["email"]
            senha = request.json["senha"]
            is_admin = request.json["is_admin"]
            novo_usuario = Usuario(nome=nome, email=email, senha=senha, is_admin=is_admin)
            resultado = cadastro_usuarios(novo_usuario)
            x = us.jsonify(resultado)
            return make_response(x, 201)
        
class UsuarioListId(Resource):
    def get(self, id):
        usuario = listar_por_id(id)
        if usuario is None:
            return make_response(jsonify('Usuario nao encontrado'), 404)
        else:
            us = UsuarioSchema()
            resulado = us.jsonify(usuario)
            return make_response(resulado, 200)
        
    def put(self, id):
        usuario_db = listar_por_id(id)
        if usuario_db is None:
            return make_response(jsonify('Usuario nao encontrado'), 404)
        else:
            usuario = UsuarioSchema()
            validate = usuario.validate(request.json)
            if validate:
                return make_response(jsonify(validate), 400)
            else:
                nome = request.json["nome"]
                email = request.json["email"]
                senha = request.json["senha"]
                is_admin = request.json["is_admin"]
                novo_usuario = Usuario(nome=nome, email=email, senha=senha, is_admin=is_admin)
                atualizar_dados(usuario_db, novo_usuario)
                usuario_atualizado = listar_por_id(id)

                return make_response(usuario.jsonify(usuario_atualizado), 201)
        
    def delete(self, id):
        usuario_db = listar_por_id(id)
        if usuario_db is None:
            return make_response(jsonify('Usuario nao encontrado'), 404)
        else:
            deletar_usuario(usuario_db)
            return make_response(jsonify('usuario deletado'), 204)

        
api.add_resource(UsuarioList, '/usuarios')
api.add_resource(UsuarioListId, '/usuarios/<int:id>')
        


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=8000, host='localhost', debug=True)