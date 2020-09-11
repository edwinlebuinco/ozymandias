from flask import Flask,request,jsonify,make_response,render_template,url_for,session,flash,redirect
from flask_restful import Resource, Api, reqparse
import pymysql,pymongo,hashlib,requests,json,funciones
import bson
from bson.objectid import ObjectId

#Create flask object
app = Flask(__name__,static_url_path='/templates')
api = Api(app)

parser = reqparse.RequestParser()

if __name__ == '__main__':
	app.run(debug=True)

#Secret key
app.secret_key="%v(mBKQL"


#Mysql Connection
#mysql_conn = pymysql.connect(host="localhost", user="root", password="13alita1@", db="ozymandias")
#mysql_conn = pymysql.connect(host="ec2-3-128-27-244.us-east-2.compute.amazonaws.com", user="ozydev", password="13Ozymandias1@", db="ozymandias")
#mysql_conn = pymysql.connect(host="ec2-18-191-242-247.us-east-2.compute.amazonaws.com", user="ozydev", password="13Ozymandias1@", db="ozymandias")
mysql_conn = pymysql.connect(host="ec2-18-217-85-218.us-east-2.compute.amazonaws.com", user="ozydev", password="13Ozymandias1@", db="ozymandias")

#Index
@app.route('/')
def main():

	if 'session_name' in session:
		return redirect(url_for('backlog'))

	else:
		return render_template('index.html')

#Index
@app.route('/status')
def status():
	try:
		with mysql_conn:
			cursor=mysql_conn.cursor()
			return "ok"
	except pymysql.Error as e:
		d = {}
		d["_error"] = "BASE_DATOS" + str(e)
		return jsonify(d)

#Index
@app.route('/index')
def index():

	if 'session_name' in session:
		return redirect(url_for('backlog'))

	else:
		return render_template('index.html')

#LOGIN
@app.route('/login',methods=['GET','POST'])
def login():

	
	if 'session_name' in session:

		return redirect(url_for('backlog'))

	else:
		return render_template('login.html')

#PERFILAR
@app.route('/perfilar',methods=['GET','POST'])
def perfilar():

        return render_template('perfilar.html')

#PERFILAR
@app.route('/perfilarrun',methods=['GET','POST'])
def perfilarrun():
	if request.method == "POST":

		data_1 = request.form['1']

		item = requests.post('http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/perfilar?user_id=' +  session.get("session_id") + '&1=' +  data_1 ).text
		ob = json.JSONDecoder().decode(item)
		try:
			if(ob["_status"] == "ok"):
				return redirect(url_for('lista')+'?type_ozy='+data_1)
		except:
			return "error " + item

#REGISTER
@app.route('/register',methods=['GET','POST'])
def register():
	return render_template('register.html')

#REGISTER
@app.route('/getreg',methods=['GET','POST'])
def getreg():
	if request.method == "GET":
		if 'session_name' in session:
			print("Serving backlog")
			return render_template('backlog.html')
		else:
			print("Serving index")
			return render_template('index.html')
	else:
		name=request.form['name']
		ape_p=request.form['ape_p']
		ape_m=request.form['ape_m']
		email_user=request.form['email_user']
		nick=request.form['nick']
		passw=request.form['passw']
		item = requests.post('http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/signup?name=' +  str(name) + '&ape_p=' +  str(ape_p) + '&ape_m=' +  str(ape_m) + '&email_user=' +  str(email_user) + '&nick=' +  str(nick) + '&passw=' +  str(passw) ).text
		ob = json.JSONDecoder().decode(item)
		try:
			if(ob["_status"] == "ok"):
				session['session_id']=ob["_id"]
				session['session_mail']=ob["_mail"]
				session['session_name']=ob["_name"]
				return redirect(url_for('perfilar'))
		except:
			try:
				if(ob["_error"] == "USUARIO_NICKNAME_EXISTE"):
					return "usuario o nickname ya existen"
			except:
				return "error"

class HelloWorld(Resource):
	def get(self, name):
		return {'hello': name}

api.add_resource(HelloWorld, '/hello/<name>')


class userlogin(Resource):
	def post(self):
		parser.add_argument('quote', type=str)
		args = parser.parse_args()

		return {
			'status': True,
			'quote': '{} added. Good'.format(args['quote'])
		}

api.add_resource(userlogin, '/testing')

class ApiLogin(Resource):
	def post(self):
		parser.add_argument('usuario', type=str)
		parser.add_argument('passwd', type=str)
		args = parser.parse_args()
		usr=args["usuario"]
		pwd=args["passwd"].encode('utf-8')
		pwd=hashlib.sha256(pwd).hexdigest()
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT id,correo,nickname FROM usuarios WHERE (correo=%s AND contrasena=%s) OR (nickname=%s AND contrasena=%s)"
				cursor.execute(sql,(usr,pwd,usr,pwd))
				result=cursor.fetchone()
				d = {}

				if(result!=None):
					d["_status"] = "ok"
					d["_id"] = str(result[0])
					d["_mail"] = result[1]
					d["_name"] = result[2]
					return jsonify(d)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(d)

api.add_resource(ApiLogin, '/api/login')

class ApiSignUp(Resource):
	def post(self):
		parser.add_argument('name', type=str)
		parser.add_argument('ape_p', type=str)
		parser.add_argument('ape_m', type=str)
		parser.add_argument('email_user', type=str)
		parser.add_argument('nick', type=str)
		parser.add_argument('passw', type=str)
		args = parser.parse_args()

		name = args["name"]
		ape_p = args["ape_p"]
		ape_m = args["ape_m"]
		email_user = args["email_user"]
		nick = args["nick"]
		passw=args["passw"].encode('utf-8')
		passw=hashlib.sha256(passw).hexdigest()
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT id,correo,nickname FROM usuarios WHERE correo=%s OR nickname=%s"
				cursor.execute(sql,(email_user,nick))
				result=cursor.fetchone()
				d = {}

				if(result!=None):
					d["_error"] = "USUARIO_NICKNAME_EXISTE"
					return jsonify(d)

				else:
					cursor = mysql_conn.cursor()
					sql = "INSERT INTO `usuarios` (`nickname`, `correo`, `contrasena`, `nombres`, `apellido_p`, `apellido_m`, `comentarios`) VALUES ('" + nick + "', '" + email_user + "', '" + passw + "', '" + name + "', '" + ape_p + "', '" + ape_m + "', '')"
					cursor.execute(sql)
					mysql_conn.commit()

					sql = "SELECT id,correo,nickname FROM usuarios WHERE correo=%s"
					cursor.execute(sql,(email_user))
					result=cursor.fetchone()
					cursor.close()
					d = {}
					d["_status"] = "ok"
					d["_id"] = str(result[0])
					d["_mail"] = result[1]
					d["_name"] = result[2]

					return jsonify(d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(d)

api.add_resource(ApiSignUp, '/api/signup')

class ApiPerfilar(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('1', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		data_1=args["1"]
		
		try:
			cur = mysql_conn.cursor()
			sql = "INSERT INTO `usuario_propiedad` (`usuario_id`, `propiedad_id`, `valor`) VALUES ('" + user_id + "', '1', '" + data_1 + "')"
			cur.execute(sql)
			mysql_conn.commit()

			cur.close()
			d = {}
			d["_status"] = "ok"
			return jsonify(d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS"
			return jsonify(d)

api.add_resource(ApiPerfilar, '/api/perfilar')

class GetPelisAll(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM peliculas WHERE id NOT IN (SELECT id_peliculas FROM calificaciones WHERE id_usuario = " + user_id + " AND id_peliculas IS NOT NULL) AND id NOT IN (SELECT pelicula_id FROM usuario_backlog WHERE usuario_id = " + user_id + " AND pelicula_id IS NOT NULL) AND id NOT IN (SELECT pelicula_id FROM usuario_no_interesa WHERE usuario_id = " + user_id + " AND pelicula_id IS NOT NULL) ORDER BY calificacion_general DESC LIMIT 100"
				cursor.execute(sql)
				rows = cursor.fetchall()

				if(rows!=None):
					return jsonify(results = rows)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetPelisAll, '/api/getpelisall/<user_id>')

class GetVideojuegosAll(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM videojuegos WHERE id NOT IN (SELECT id_videojuegos FROM calificaciones WHERE id_usuario = " + user_id + " AND id_videojuegos IS NOT NULL) AND id NOT IN (SELECT videojuego_id FROM usuario_backlog WHERE usuario_id = " + user_id + " AND videojuego_id IS NOT NULL) AND id NOT IN (SELECT videojuego_id FROM usuario_no_interesa WHERE usuario_id = " + user_id + " AND videojuego_id IS NOT NULL) ORDER BY calificacion_general DESC LIMIT 100"
				cursor.execute(sql)
				rows = cursor.fetchall()

				if(rows!=None):
					return jsonify(results = rows)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetVideojuegosAll, '/api/getvideojuegosall/<user_id>')

class GetVideojuegosAllMongo(Resource):
	def get(self):
		return "mongodb"

api.add_resource(GetVideojuegosAllMongo, '/api/getvideojuegosallmongo')

class GetLibrosAll(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM libros WHERE id NOT IN (SELECT id_libro FROM calificaciones WHERE id_usuario = " + user_id + " AND id_libro IS NOT NULL) AND id NOT IN (SELECT libro_id FROM usuario_backlog WHERE usuario_id = " + user_id + " AND libro_id IS NOT NULL) AND id NOT IN (SELECT libro_id FROM usuario_no_interesa WHERE usuario_id = " + user_id + " AND libro_id IS NOT NULL) ORDER BY calificacion_general DESC LIMIT 100"
				cursor.execute(sql)
				rows = cursor.fetchall()

				if(rows!=None):
					return jsonify(results = rows)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetLibrosAll, '/api/getlibrosall/<user_id>')

class ApiVGAddCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('videojuego_id', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		videojuego_id=args["videojuego_id"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `calificaciones` (`id_usuario`, `id_videojuegos`, `calificacion`, `fecha_calificacion`) VALUES ('" + user_id + "', '" + videojuego_id + "', '" + calificacion + "', now())"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiVGAddCali, '/api/addvjcali')

class ApiMDBAddCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('ozy_id', type=str)
		parser.add_argument('typeozy', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		ozy_id=args["ozy_id"]
		typeozy=args["typeozy"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `calificaciones_mdb` (`id_usuario`, `id_ozy`, `typeozy`, `calificacion`, `fecha_calificacion`) VALUES ('" + user_id + "', '" + ozy_id + "', '" + typeozy + "', '" + calificacion + "', now())"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiMDBAddCali, '/api/addmdbcali')

class ApiPEAddCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('pelicula_id', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		pelicula_id=args["pelicula_id"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `calificaciones` (`id_usuario`, `id_peliculas`, `calificacion`, `fecha_calificacion`) VALUES ('" + user_id + "', '" + pelicula_id + "', '" + calificacion + "', now())"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiPEAddCali, '/api/addpecali')

class ApiLIAddCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('libro_id', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		libro_id=args["libro_id"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `calificaciones` (`id_usuario`, `id_libro`, `calificacion`, `fecha_calificacion`) VALUES ('" + user_id + "', '" + libro_id + "', '" + calificacion + "', now())"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiLIAddCali, '/api/addlicali')

class ApiVGDelCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('videojuego_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		videojuego_id=args["videojuego_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `calificaciones` WHERE `id_usuario` = '" + user_id + "' AND `id_videojuegos` = '" + videojuego_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiVGDelCali, '/api/delvjcali')

class ApiPEDelCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('pelicula_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		pelicula_id=args["pelicula_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `calificaciones` WHERE `id_usuario` = '" + user_id + "' AND `id_peliculas` = '" + pelicula_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiPEDelCali, '/api/delpecali')

class ApiLIDelCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('libro_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		libro_id=args["libro_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `calificaciones` WHERE `id_usuario` = '" + user_id + "' AND `id_libro` = '" + libro_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiLIDelCali, '/api/dellicali')

class ApiVGUpdCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('videojuego_id', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		videojuego_id=args["videojuego_id"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "UPDATE `calificaciones` SET `calificacion` = '" + calificacion + "' WHERE `id_usuario` = '" + user_id + "' AND `id_videojuegos` = '" + videojuego_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiVGUpdCali, '/api/updvjcali')

class ApiPEUpdCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('pelicula_id', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		pelicula_id=args["pelicula_id"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "UPDATE `calificaciones` SET `calificacion` = '" + calificacion + "' WHERE `id_usuario` = '" + user_id + "' AND `id_peliculas` = '" + pelicula_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiPEUpdCali, '/api/updpecali')

class ApiLIUpdCali(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('libro_id', type=str)
		parser.add_argument('calificacion', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		libro_id=args["libro_id"]
		calificacion=args["calificacion"]

		cur = mysql_conn.cursor()
		sql = "UPDATE `calificaciones` SET `calificacion` = '" + calificacion + "' WHERE `id_usuario` = '" + user_id + "' AND `id_libro` = '" + libro_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiLIUpdCali, '/api/updlicali')

class ApiVGAddBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('videojuego_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		videojuego_id=args["videojuego_id"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_backlog` (`usuario_id`, `videojuego_id`) VALUES ('" + user_id + "', '" + videojuego_id + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiVGAddBL, '/api/addvjbl')

class ApiAddMDBBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('ozy_id', type=str)
		parser.add_argument('typeozy', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		ozy_id=args["ozy_id"]
		typeozy=args["typeozy"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_backlog_mdb` (`usuario_id`, `ozy_id`, `typeozy`) VALUES ('" + user_id + "', '" + ozy_id + "', '" + typeozy + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiAddMDBBL, '/api/addmdbbl')

class ApiAddMDBNeg(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('ozy_id', type=str)
		parser.add_argument('typeozy', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		ozy_id=args["ozy_id"]
		typeozy=args["typeozy"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_no_interesa_mdb` (`usuario_id`, `ozy_id`, `typeozy`) VALUES ('" + user_id + "', '" + ozy_id + "', '" + typeozy + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiAddMDBNeg, '/api/addmdbneg')

class ApiVGAddNeg(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('videojuego_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		videojuego_id=args["videojuego_id"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_no_interesa` (`usuario_id`, `videojuego_id`) VALUES ('" + user_id + "', '" + videojuego_id + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiVGAddNeg, '/api/addvjneg')

class ApiPEAddBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('pelicula_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		pelicula_id=args["pelicula_id"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_backlog` (`usuario_id`, `pelicula_id`) VALUES ('" + user_id + "', '" + pelicula_id + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiPEAddBL, '/api/addpebl')

class ApiPEAddNeg(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('pelicula_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		pelicula_id=args["pelicula_id"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_no_interesa` (`usuario_id`, `pelicula_id`) VALUES ('" + user_id + "', '" + pelicula_id + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiPEAddNeg, '/api/addpeneg')

class ApiLIAddBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('libro_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		libro_id=args["libro_id"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_backlog` (`usuario_id`, `libro_id`) VALUES ('" + user_id + "', '" + libro_id + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiLIAddBL, '/api/addlibl')

class ApiLIAddNeg(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('libro_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		libro_id=args["libro_id"]

		cur = mysql_conn.cursor()
		sql = "INSERT INTO `usuario_no_interesa` (`usuario_id`, `libro_id`) VALUES ('" + user_id + "', '" + libro_id + "')"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiLIAddNeg, '/api/addlineg')

class ApiVGDelBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('videojuego_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		videojuego_id=args["videojuego_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `usuario_backlog` WHERE `usuario_id` = '" + user_id + "' AND `videojuego_id` = '" + videojuego_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiVGDelBL, '/api/delvjbl')

class ApiPEDelBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('pelicula_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		pelicula_id=args["pelicula_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `usuario_backlog` WHERE `usuario_id` = '" + user_id + "' AND `pelicula_id` = '" + pelicula_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiPEDelBL, '/api/delpebl')

class ApiLIDelBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('libro_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		libro_id=args["libro_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `usuario_backlog` WHERE `usuario_id` = '" + user_id + "' AND `libro_id` = '" + libro_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiLIDelBL, '/api/dellibl')

class ApiMDBDelBL(Resource):
	def post(self):
		parser.add_argument('user_id', type=str)
		parser.add_argument('ozy_id', type=str)
		args = parser.parse_args()
		user_id=args["user_id"]
		ozy_id=args["ozy_id"]

		cur = mysql_conn.cursor()
		sql = "DELETE FROM `usuario_backlog_mdb` WHERE `usuario_id` = '" + user_id + "' AND `ozy_id` = '" + ozy_id + "'"
		cur.execute(sql)
		mysql_conn.commit()
		cur.close()
		d = {}
		d["_status"] = "ok"
		return jsonify(d)

api.add_resource(ApiMDBDelBL, '/api/delmdbbl')

class GetBL(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM `usuario_backlog` WHERE `usuario_id` = '" + user_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()
				items = []

				if(rows!=None):
					for i, row in enumerate(rows):
						if(row[2]!=None):
							item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getvideojuego/' + str( row[2] ) ).text
							ob_vj = json.JSONDecoder().decode(item)
							arreglo = {}
							arreglo["_tipo"] = "videojuego"
							arreglo["_id"] = ob_vj["results"][0][0]
							arreglo["_nombre"] = ob_vj["results"][0][1]
							arreglo["_cali"] = round(ob_vj["results"][0][8],1)
							items.append(arreglo)
							#items[i] = str( row[2] )
						if(row[4]!=None):
							item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getpelicula/' + str( row[4] ) ).text
							ob_pe = json.JSONDecoder().decode(item)
							arreglo = {}
							arreglo["_tipo"] = "pelicula"
							arreglo["_id"] = ob_pe["results"][0][0]
							arreglo["_nombre"] = ob_pe["results"][0][1]
							arreglo["_cali"] = round(ob_pe["results"][0][8],1)
							items.append(arreglo)
							#items[i] = str( row[2] )
						if(row[3]!=None):
							item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getlibro/' + str( row[3] ) ).text
							ob_pe = json.JSONDecoder().decode(item)
							arreglo = {}
							arreglo["_tipo"] = "libro"
							arreglo["_id"] = ob_pe["results"][0][0]
							arreglo["_nombre"] = ob_pe["results"][0][1]
							arreglo["_cali"] = round(ob_pe["results"][0][7],1)
							items.append(arreglo)
							#items[i] = str( row[2] )
					return jsonify(results = items)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetBL, '/api/getbl/<user_id>')

class GetBLMDB(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT ozy_id FROM `usuario_backlog_mdb` WHERE `usuario_id` = '" + user_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()

				if(rows!=None):
					items = []
					for i, row in enumerate(rows):
						items.append( { "_id" : {"$eq": ObjectId(str(row[0])) } }  )

					#MongoDB Connection
					ob_results = []
					myclient = pymongo.MongoClient("mongodb://localhost:27017/")
					mydb = myclient["ozymandias"]
					mycol = mydb["ozys"]
					#valores = mycol.find({  "$and":  items  })
					for x in mycol.find({  "$or":  items  }):
						d = {}
						d["id"] = str(x['_id'])
						d["nombre"] = x['name']
						if ( x['@type'] == "Review" ):
							d["tipo"] = "Book"
							d["rating"] = str ( x["reviewRating"]["ratingValue"] )
						elif( x['@type'] == "Movie" ):
							d["tipo"] = x['@type']
							d["rating"] = str ( round(float(x["aggregateRating"]["ratingValue"]) / 2, 1 ) )
						elif( x['@type'] == "VideoGame" ):
							d["tipo"] = x['@type']
							d["rating"] = str ( round(int(x["aggregateRating"]["ratingValue"]) / 20, 1 ) )
						ob_results.append( d )

					return jsonify(results = ob_results)

				else:
					d={}
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = [])

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetBLMDB, '/api/getblmdb/<user_id>')

class GetCaliMDB(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT id_ozy,calificacion,DATE_FORMAT(fecha_calificacion, '%d/%m/%Y') FROM `calificaciones_mdb` WHERE `id_usuario` = '" + user_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()

				if(rows!=None):
					items = []
					for i, row in enumerate(rows):
						items.append( { "_id" : {"$eq": ObjectId(str(row[0])) } }  )

					#MongoDB Connection
					ob_results = []
					myclient = pymongo.MongoClient("mongodb://localhost:27017/")
					mydb = myclient["ozymandias"]
					mycol = mydb["ozys"]
					#valores = mycol.find({  "$and":  items  })
					for x in mycol.find({  "$or":  items  }):
						d = {}
						d["_id"] = str(x['_id'])
						d["_nombre"] = x['name']
						for i, row in enumerate(rows):
							if ( row[0] == d["_id"] ):
								d["_cali"] = row[1]
								d["_fecha"] = row[2]
						if ( x['@type'] == "Review" ):
							d["_tipo"] = "libro"
						elif( x['@type'] == "Movie" ):
							d["_tipo"] = "pelicula"
						elif( x['@type'] == "VideoGame" ):
							d["_tipo"] = "videojuego"
						ob_results.append( d )

					return jsonify(results = ob_results)

				else:
					d={}
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = [])

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetCaliMDB, '/api/getcalimdb/<user_id>')

class GetCali(Resource):
	def get(self, user_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				#sql = "SELECT id, FROM `calificaciones` WHERE `id_usuario` = '" + user_id + "'"
				sql = "SELECT id,id_usuario,id_libro,id_peliculas,id_videojuegos,calificacion,DATE_FORMAT(fecha_calificacion, '%d/%m/%Y') FROM `calificaciones` WHERE `id_usuario` = '" + user_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()
				items = []

				if(rows!=None):
					for i, row in enumerate(rows):
						if(row[4]!=None):
							item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getvideojuego/' + str( row[4] ) ).text
							ob_vj = json.JSONDecoder().decode(item)
							arreglo = {}
							arreglo["_tipo"] = "videojuego"
							arreglo["_id"] = ob_vj["results"][0][0]
							arreglo["_nombre"] = ob_vj["results"][0][1]
							arreglo["_cali"] = row[5]
							arreglo["_fecha"] = row[6]
							items.append(arreglo)
							#items[i] = str( row[2] )
						if(row[3]!=None):
							item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getpelicula/' + str( row[3] ) ).text
							ob_pe = json.JSONDecoder().decode(item)
							arreglo = {}
							arreglo["_tipo"] = "pelicula"
							arreglo["_id"] = ob_pe["results"][0][0]
							arreglo["_nombre"] = ob_pe["results"][0][1]
							arreglo["_cali"] = row[5]
							arreglo["_fecha"] = row[6]
							items.append(arreglo)
							#items[i] = str( row[2] )
						if(row[2]!=None):
							item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getlibro/' + str( row[2] ) ).text
							ob_pe = json.JSONDecoder().decode(item)
							arreglo = {}
							arreglo["_tipo"] = "libro"
							arreglo["_id"] = ob_pe["results"][0][0]
							arreglo["_nombre"] = ob_pe["results"][0][1]
							arreglo["_cali"] = row[5]
							arreglo["_fecha"] = row[6]
							items.append(arreglo)
							#items[i] = str( row[2] )
					return jsonify(results = items)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetCali, '/api/getcali/<user_id>')

class GetVideojuego(Resource):
	def get(self, videojuego_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM `videojuegos` WHERE `id` = '" + videojuego_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()
				d = {}

				if(rows!=None):
					return jsonify(results = rows)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetVideojuego, '/api/getvideojuego/<videojuego_id>')

class GetPelicula(Resource):
	def get(self, pelicula_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM `peliculas` WHERE `id` = '" + pelicula_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()
				d = {}

				if(rows!=None):
					return jsonify(results = rows)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetPelicula, '/api/getpelicula/<pelicula_id>')

class GetLibro(Resource):
	def get(self, libro_id):
		try:

			with mysql_conn:

				cursor=mysql_conn.cursor()

				sql = "SELECT * FROM `libros` WHERE `id` = '" + libro_id + "'"
				cursor.execute(sql)
				rows = cursor.fetchall()
				d = {}

				if(rows!=None):
					return jsonify(results = rows)

				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)

		except pymysql.Error as e:

			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)

api.add_resource(GetLibro, '/api/getlibro/<libro_id>')

class CoincidenciasVJ1aN(Resource):
	def get(self, usuario_id):
		try:
			with mysql_conn:
				cursor=mysql_conn.cursor()
				sql = "SELECT id_videojuegos,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id + "' AND id_videojuegos IS NOT NULL"
				cursor.execute(sql)
				vec1 = cursor.fetchall()
				d = {}
				items = {}
				usuarios_coin = []
				if(vec1!=None):
					for i, row in enumerate(vec1):
						cursor=mysql_conn.cursor()
						sql = "SELECT id_usuario FROM `calificaciones` WHERE `id_videojuegos` = '" + str(vec1[i][0]) + "'"
						cursor.execute(sql)
						filas_coin = cursor.fetchall()
						if(filas_coin!=None):
							for i, fila_coin in enumerate(filas_coin):
								if(int( usuario_id )!=int( filas_coin[i][0] )) and (filas_coin[i][0] not in usuarios_coin):
									usuarios_coin.append(filas_coin[i][0])
									cursor=mysql_conn.cursor()
									sql = "SELECT id_videojuegos,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + str(filas_coin[i][0]) + "' AND id_videojuegos IS NOT NULL"
									cursor.execute(sql)
									vec2 = cursor.fetchall()
									total = funciones.Coincidencias(vec1,vec2)
									d[ str(filas_coin[i][0]) ] = total
									items[ str(filas_coin[i][0]) ] = [ total, vec2 ]
					recomendaciones = funciones.ListaRecomendados(items)
					return jsonify(recomendaciones)
				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)
api.add_resource(CoincidenciasVJ1aN, '/api/coincidenciasvj1an/<usuario_id>')

class CoincidenciasVJ1a1(Resource):
	def get(self, usuario_id,usuario_id_2):
		try:
			with mysql_conn:
				cursor=mysql_conn.cursor()
				sql = "SELECT id_videojuegos,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id + "' AND id_videojuegos IS NOT NULL"
				cursor.execute(sql)
				vec1 = cursor.fetchall()
				cursor=mysql_conn.cursor()
				sql = "SELECT id_videojuegos,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id_2 + "' AND id_videojuegos IS NOT NULL"
				cursor.execute(sql)
				vec2 = cursor.fetchall()
				d = {}
				if(vec1!=None) and (vec2!=None):
					return jsonify(result = funciones.Coincidencias(vec1,vec2))
				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(result = d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)
api.add_resource(CoincidenciasVJ1a1, '/api/coincidenciasvj1a1/<usuario_id>/<usuario_id_2>')

class CoincidenciasLI1aN(Resource):
	def get(self, usuario_id):
		try:
			with mysql_conn:
				cursor=mysql_conn.cursor()
				sql = "SELECT id_libro,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id + "' AND id_libro IS NOT NULL"
				cursor.execute(sql)
				vec1 = cursor.fetchall()
				d = {}
				items = {}
				usuarios_coin = []
				if(vec1!=None):
					for i, row in enumerate(vec1):
						cursor=mysql_conn.cursor()
						sql = "SELECT id_usuario FROM `calificaciones` WHERE `id_libro` = '" + str(vec1[i][0]) + "'"
						cursor.execute(sql)
						filas_coin = cursor.fetchall()
						if(filas_coin!=None):
							for i, fila_coin in enumerate(filas_coin):
								if(int( usuario_id )!=int( filas_coin[i][0] )) and (filas_coin[i][0] not in usuarios_coin):
									usuarios_coin.append(filas_coin[i][0])
									cursor=mysql_conn.cursor()
									sql = "SELECT id_libro,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + str(filas_coin[i][0]) + "' AND id_libro IS NOT NULL"
									cursor.execute(sql)
									vec2 = cursor.fetchall()
									total = funciones.Coincidencias(vec1,vec2)
									d[ str(filas_coin[i][0]) ] = total
									items[ str(filas_coin[i][0]) ] = [ total, vec2 ]
					recomendaciones = funciones.ListaRecomendados(items)
					return jsonify(recomendaciones)
				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)
api.add_resource(CoincidenciasLI1aN, '/api/coincidenciasli1an/<usuario_id>')

class CoincidenciasLI1a1(Resource):
	def get(self, usuario_id,usuario_id_2):
		try:
			with mysql_conn:
				cursor=mysql_conn.cursor()
				sql = "SELECT id_libro,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id + "' AND id_libro IS NOT NULL"
				cursor.execute(sql)
				vec1 = cursor.fetchall()
				cursor=mysql_conn.cursor()
				sql = "SELECT id_libro,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id_2 + "' AND id_libro IS NOT NULL"
				cursor.execute(sql)
				vec2 = cursor.fetchall()
				d = {}
				if(vec1!=None) and (vec2!=None):
					return jsonify(result = funciones.Coincidencias(vec1,vec2))
				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(result = d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)
api.add_resource(CoincidenciasLI1a1, '/api/coincidenciasli1a1/<usuario_id>/<usuario_id_2>')


class CoincidenciasPE1aN(Resource):
	def get(self, usuario_id):
		try:
			with mysql_conn:
				cursor=mysql_conn.cursor()
				sql = "SELECT id_peliculas,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id + "' AND id_peliculas IS NOT NULL"
				cursor.execute(sql)
				vec1 = cursor.fetchall()
				d = {}
				items = {}
				usuarios_coin = []
				if(vec1!=None):
					for i, row in enumerate(vec1):
						cursor=mysql_conn.cursor()
						sql = "SELECT id_usuario FROM `calificaciones` WHERE `id_peliculas` = '" + str(vec1[i][0]) + "'"
						cursor.execute(sql)
						filas_coin = cursor.fetchall()
						if(filas_coin!=None):
							for i, fila_coin in enumerate(filas_coin):
								if(int( usuario_id )!=int( filas_coin[i][0] )) and (filas_coin[i][0] not in usuarios_coin):
									usuarios_coin.append(filas_coin[i][0])
									cursor=mysql_conn.cursor()
									sql = "SELECT id_peliculas,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + str(filas_coin[i][0]) + "' AND id_peliculas IS NOT NULL"
									cursor.execute(sql)
									vec2 = cursor.fetchall()
									total = funciones.Coincidencias(vec1,vec2)
									d[ str(filas_coin[i][0]) ] = total
									items[ str(filas_coin[i][0]) ] = [ total, vec2 ]
					recomendaciones = funciones.ListaRecomendados(items)
					return jsonify(recomendaciones)
				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(results = d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)
api.add_resource(CoincidenciasPE1aN, '/api/coincidenciaspe1an/<usuario_id>')

class CoincidenciasPE1a1(Resource):
	def get(self, usuario_id,usuario_id_2):
		try:
			with mysql_conn:
				cursor=mysql_conn.cursor()
				sql = "SELECT id_peliculas,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id + "' AND id_peliculas IS NOT NULL"
				cursor.execute(sql)
				vec1 = cursor.fetchall()
				cursor=mysql_conn.cursor()
				sql = "SELECT id_peliculas,calificacion FROM `calificaciones` WHERE `id_usuario` = '" + usuario_id_2 + "' AND id_peliculas IS NOT NULL"
				cursor.execute(sql)
				vec2 = cursor.fetchall()
				d = {}
				if(vec1!=None) and (vec2!=None):
					return jsonify(result = funciones.Coincidencias(vec1,vec2))
				else:
					d["_error"] = "DATOS_INCORRECTOS"
					return jsonify(result = d)
		except pymysql.Error as e:
			d = {}
			d["_error"] = "BASE_DATOS" + str(e)
			return jsonify(results = d)
api.add_resource(CoincidenciasPE1a1, '/api/coincidenciaspe1a1/<usuario_id>/<usuario_id_2>')


@app.route('/url')
def get_data():
	#return requests.get('http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/hello/edwin').content
	#return requests.post('http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/testing?quote=edwin').content
	return requests.post('http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/perfilar?user_id=' +  session.get("session_id") + '&1=0&2=0&3=0&4=0&5=0&6=0&7=0&8=0&9=0&').content


#LOGIN
@app.route('/getinlog',methods=['GET','POST'])
def getinlog():
	if request.method == "GET":
		if 'session_name' in session:
			print("Serving backlog")
			return render_template('backlog.html')
		else:
			print("Serving index")
			return render_template('index.html')
	else:
		usr=request.form['usuario']
		pwd=request.form['passwd']
		item = requests.post('http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/login?usuario=' +  str(usr) + '&passwd=' + str(pwd)).text
		ob = json.JSONDecoder().decode(item)
		try:
			if(ob["_status"] == "ok"):
				session['session_id']=ob["_id"]
				session['session_mail']=ob["_mail"]
				session['session_name']=ob["_name"]
				return redirect(url_for('backlog'))
		except:
			try:
				if(ob["_error"] == "DATOS_INCORRECTOS"):
					return "datos incorrectos"
			except:
				return "error"
#ADDVJCALI
@app.route('/addvjcali',methods=['GET','POST'])
def addvjcali():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			calificacion = request.args["cali"]

			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delvjbl?user_id=' +  session.get("session_id") + '&videojuego_id=' + id_vj ).text
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addvjcali?user_id=' +  session.get("session_id") + '&videojuego_id=' + id_vj + '&calificacion=' + calificacion ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('historic'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))
#ADDVJMDBCALI
@app.route('/addvjmdbcali',methods=['GET','POST'])
def addvjmdbcali():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			calificacion = request.args["cali"]

			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_vj ).text
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbcali?user_id=' +  session.get("session_id") + '&ozy_id=' + id_vj + '&calificacion=' + calificacion + '&typeozy=vj' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('historic'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDLICALI
@app.route('/addlicali',methods=['GET','POST'])
def addlicali():
	if request.method == "GET":
		if 'session_name' in session:
			id_li = request.args["id"]
			calificacion = request.args["cali"]

			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/dellibl?user_id=' +  session.get("session_id") + '&libro_id=' + id_li ).text
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addlicali?user_id=' +  session.get("session_id") + '&libro_id=' + id_li + '&calificacion=' + calificacion ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('historic'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDLIMDBCALI
@app.route('/addlimdbcali',methods=['GET','POST'])
def addlimdbcali():
	if request.method == "GET":
		if 'session_name' in session:
			id_li = request.args["id"]
			calificacion = request.args["cali"]

			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_li ).text
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbcali?user_id=' +  session.get("session_id") + '&ozy_id=' + id_li + '&calificacion=' + calificacion + '&typeozy=li' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('historic'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDPECALI
@app.route('/addpecali',methods=['GET','POST'])
def addpecali():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			calificacion = request.args["cali"]

			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delpebl?user_id=' +  session.get("session_id") + '&pelicula_id=' + id_pe ).text
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addpecali?user_id=' +  session.get("session_id") + '&pelicula_id=' + id_pe + '&calificacion=' + calificacion ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('historic'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDPEMDBCALI
@app.route('/addpemdbcali',methods=['GET','POST'])
def addpemdbcali():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			calificacion = request.args["cali"]

			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_pe ).text
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbcali?user_id=' +  session.get("session_id") + '&ozy_id=' + id_pe + '&calificacion=' + calificacion + '&typeozy=pe' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('historic'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDVJBL
@app.route('/addvjbl',methods=['GET','POST'])
def addvjbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addvjbl?user_id=' +  session.get("session_id") + '&videojuego_id=' + id_vj ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDVJMDBBL
@app.route('/addvjmdbbl',methods=['GET','POST'])
def addvjmdbbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_ = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_ + '&typeozy=vj' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDVJNEG
@app.route('/addvjneg',methods=['GET','POST'])
def addvjneg():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addvjneg?user_id=' +  session.get("session_id") + '&videojuego_id=' + id_vj ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDVJMDBNEG
@app.route('/addvjmdbneg',methods=['GET','POST'])
def addvjmdbneg():
	if request.method == "GET":
		if 'session_name' in session:
			id_ = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbneg?user_id=' +  session.get("session_id") + '&ozy_id=' + id_ + '&typeozy=vj' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDLIBL
@app.route('/addlibl',methods=['GET','POST'])
def addlibl():
	if request.method == "GET":
		if 'session_name' in session:
			id_li = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addlibl?user_id=' +  session.get("session_id") + '&libro_id=' + id_li ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDLIMDBBL
@app.route('/addlimdbbl',methods=['GET','POST'])
def addlimdbbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_ = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_ + '&typeozy=li' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDLINEG
@app.route('/addlineg',methods=['GET','POST'])
def addlineg():
	if request.method == "GET":
		if 'session_name' in session:
			id_li = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addlineg?user_id=' +  session.get("session_id") + '&libro_id=' + id_li ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDLIMDBNEG
@app.route('/addlimdbneg',methods=['GET','POST'])
def addlimdbneg():
	if request.method == "GET":
		if 'session_name' in session:
			id_ = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbneg?user_id=' +  session.get("session_id") + '&ozy_id=' + id_ + '&typeozy=li' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDPEJBL
@app.route('/addpebl',methods=['GET','POST'])
def addpebl():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addpebl?user_id=' +  session.get("session_id") + '&pelicula_id=' + id_pe ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDPEMDBBL
@app.route('/addpemdbbl',methods=['GET','POST'])
def addpemdbbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_ = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_ + '&typeozy=pe' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDPENEG
@app.route('/addpeneg',methods=['GET','POST'])
def addpeneg():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addpeneg?user_id=' +  session.get("session_id") + '&pelicula_id=' + id_pe ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#ADDPEMDBNEG
@app.route('/addpemdbneg',methods=['GET','POST'])
def addpemdbneg():
	if request.method == "GET":
		if 'session_name' in session:
			id_ = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/addmdbneg?user_id=' +  session.get("session_id") + '&ozy_id=' + id_ + '&typeozy=pe' ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return "ok"#redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#DELVJBL
@app.route('/delvjbl',methods=['GET','POST'])
def delvjbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delvjbl?user_id=' +  session.get("session_id") + '&videojuego_id=' + id_vj ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#DELVJMDBBL
@app.route('/delvjmdbbl',methods=['GET','POST'])
def delvjmdbbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_vj ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('backlogmdb'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#DELLIBL
@app.route('/dellibl',methods=['GET','POST'])
def dellibl():
	if request.method == "GET":
		if 'session_name' in session:
			id_li = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/dellibl?user_id=' +  session.get("session_id") + '&libro_id=' + id_li ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#DELLIMDBBL
@app.route('/dellimdbbl',methods=['GET','POST'])
def dellimdbbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_li = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_li ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('backlogmdb'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#DELPEBL
@app.route('/delpebl',methods=['GET','POST'])
def delpebl():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delpebl?user_id=' +  session.get("session_id") + '&pelicula_id=' + id_pe ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('backlog'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#DELPEMDBBL
@app.route('/delpemdbbl',methods=['GET','POST'])
def delpemdbbl():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			item = requests.post( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/delmdbbl?user_id=' +  session.get("session_id") + '&ozy_id=' + id_pe ).text
			ob = json.JSONDecoder().decode(item)
			try:
				if(ob["_status"] == "ok"):
					return redirect(url_for('backlogmdb'))
			except:
				return "error"
		else:
			return redirect(url_for('index'))

#Backlog
@app.route('/backlogback')
def backlogback():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getbl/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]
		return render_template ('backlog.html', len = len(ob_results), ob_results = ob_results)

	else:

		return render_template('index.html')	

#Backlogmdb
@app.route('/backlog')
def backlog():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getblmdb/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]
		#return "hola"
		return render_template ('backlogmdb.html', len = len(ob_results), ob_results = ob_results)

	else:

		return render_template('index.html')	

#Historicback
@app.route('/historicback')
def historicback():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getcali/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]
		return render_template ('historic.html', len = len(ob_results), ob_results = ob_results)

	else:

		return render_template('index.html')	

#Historic
@app.route('/historic')
def historic():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getcalimdb/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]
		return render_template ('historic.html', len = len(ob_results), ob_results = ob_results)

	else:

		return render_template('index.html')	

#LISTA
@app.route('/lista',methods=['GET','POST'])
def lista():

	if 'session_name' in session:
		if request.method == "GET":
			type_ozy = request.args["type_ozy"]
			if(type_ozy == "0"):
				item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getpelisall/' + str( session['session_id'] ) ).text
				ob = json.JSONDecoder().decode(item)
				ob_results = ob["results"]
				return render_template ('peliculas_p.html', len = len(ob_results), ob_results = ob_results)
			elif(type_ozy == "1"):
				item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getlibrosall/' + str( session['session_id'] ) ).text
				ob = json.JSONDecoder().decode(item)
				ob_results = ob["results"]
				return render_template ('libros_p.html', len = len(ob_results), ob_results = ob_results)
			elif(type_ozy == "2"):
				item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getvideojuegosall/' + str( session['session_id'] ) ).text
				ob = json.JSONDecoder().decode(item)
				ob_results = ob["results"]
				return render_template ('videojuegos_p.html', len = len(ob_results), ob_results = ob_results)

	else:

		return render_template('index.html')	

#LISTA
@app.route('/videojuegos')
def videojuegos():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getvideojuegosall/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/coincidenciasvj1an/' + str( session['session_id'] ) ).text
		ob_reco = json.JSONDecoder().decode(item)
		ob_reco_mx = []

		if len(ob_reco)>20:
			lenmax = 20
		else:
			lenmax = len(ob_reco)
		for i in range(0, lenmax):
			item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getvideojuego/' + str(ob_reco[i][0]) ).text
			ob = json.JSONDecoder().decode(item)
			ob_reco_mx.append(ob["results"])

		return render_template ('videojuegos.html', len = len(ob_results), ob_results = ob_results, len_mx = len(ob_reco_mx), ob_reco_mx = ob_reco_mx)
		#return render_template ('videojuegos.html', len = len(ob_results), ob_results = ob_results)
		#return jsonify(ob_reco_mx)

	else:

		return render_template('index.html')	

#LISTA
@app.route('/videojuegosmongo')
def videojuegosmongo():

	if 'session_name' in session:

		items = []
		
		cursor = mysql_conn.cursor()
		sql = "SELECT ozy_id FROM `usuario_backlog_mdb` WHERE `usuario_id` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		cursor = mysql_conn.cursor()
		sql = "SELECT ozy_id FROM `usuario_no_interesa_mdb` WHERE `usuario_id` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		cursor = mysql_conn.cursor()
		sql = "SELECT id_ozy FROM `calificaciones_mdb` WHERE `id_usuario` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		#MongoDB Connection
		ob_results = []
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["ozymandias"]
		mycol = mydb["ozys"]
		items.append( {"@type":"VideoGame"}  )
		for x in mycol.find({  "$and":  items  }).limit(100):
			ob_results.append( x )
		#return ob[0]
		#return render_template ('videojuegos.html', len = len(ob_results), ob_results = ob_results, len_mx = len(ob_reco_mx), ob_reco_mx = ob_reco_mx)
		return render_template ('videojuegosmongo.html', len = len(ob_results), ob_results = ob_results)
		#return jsonify(ob[0]["name"])
		#return str(ob_results[0]["_id"])
	else:

		return render_template('index.html')	

#LISTA
@app.route('/libros')
def libros():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getlibrosall/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/coincidenciasli1an/' + str( session['session_id'] ) ).text
		ob_reco = json.JSONDecoder().decode(item)
		ob_reco_mx = []

		if len(ob_reco)>20:
			lenmax = 20
		else:
			lenmax = len(ob_reco)
		for i in range(0, lenmax):
			item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getlibro/' + str(ob_reco[i][0]) ).text
			ob = json.JSONDecoder().decode(item)
			ob_reco_mx.append(ob["results"])

		return render_template ('libros.html', len = len(ob_results), ob_results = ob_results, len_mx = len(ob_reco_mx), ob_reco_mx = ob_reco_mx)
		#return render_template ('libros.html', len = len(ob_results), ob_results = ob_results)
		#return "se realizo el get " + item

	else:

		return render_template('index.html')	

#LISTA
@app.route('/librosmongo')
def librosmongo():

	if 'session_name' in session:

		items = []
		
		cursor = mysql_conn.cursor()
		sql = "SELECT ozy_id FROM `usuario_backlog_mdb` WHERE `usuario_id` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		cursor = mysql_conn.cursor()
		sql = "SELECT ozy_id FROM `usuario_no_interesa_mdb` WHERE `usuario_id` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		cursor = mysql_conn.cursor()
		sql = "SELECT id_ozy FROM `calificaciones_mdb` WHERE `id_usuario` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		#MongoDB Connection
		ob_results = []
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["ozymandias"]
		mycol = mydb["ozys"]
		items.append( {"@type":"Review"}  )
		for x in mycol.find({  "$and":  items  }).limit(100):
			ob_results.append( x )
		#return ob[0]
		#return render_template ('libros.html', len = len(ob_results), ob_results = ob_results, len_mx = len(ob_reco_mx), ob_reco_mx = ob_reco_mx)
		return render_template ('librosmongo.html', len = len(ob_results), ob_results = ob_results)
		#return jsonify(ob[0]["name"])
		#return str(ob_results[0]["_id"])
	else:

		return render_template('index.html')	

#LISTA
@app.route('/peliculas')
def peliculas():

	if 'session_name' in session:

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getpelisall/' + str( session['session_id'] ) ).text
		ob = json.JSONDecoder().decode(item)
		ob_results = ob["results"]

		item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/coincidenciaspe1an/' + str( session['session_id'] ) ).text
		ob_reco = json.JSONDecoder().decode(item)
		ob_reco_mx = []

		if len(ob_reco)>20:
			lenmax = 20
		else:
			lenmax = len(ob_reco)
		for i in range(0, lenmax):
			item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getpelicula/' + str(ob_reco[i][0]) ).text
			ob = json.JSONDecoder().decode(item)
			ob_reco_mx.append(ob["results"])

		return render_template ('peliculas.html', len = len(ob_results), ob_results = ob_results, len_mx = len(ob_reco_mx), ob_reco_mx = ob_reco_mx)
		#return render_template ('peliculas.html', len = len(ob_results), ob_results = ob_results)
		#return "se realizo el get " + item

	else:

		return render_template('index.html')	

#LISTA
@app.route('/peliculasmongo')
def peliculasmongo():

	if 'session_name' in session:

		items = []
		
		cursor = mysql_conn.cursor()
		sql = "SELECT ozy_id FROM `usuario_backlog_mdb` WHERE `usuario_id` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		cursor = mysql_conn.cursor()
		sql = "SELECT ozy_id FROM `usuario_no_interesa_mdb` WHERE `usuario_id` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		cursor = mysql_conn.cursor()
		sql = "SELECT id_ozy FROM `calificaciones_mdb` WHERE `id_usuario` = '" + str( session['session_id'] ) + "'"
		cursor.execute(sql)
		rows = cursor.fetchall()
		if(rows!=None):
			for i, row in enumerate(rows):
				#items.append( ObjectId(str(row[0])) )
				items.append( { "_id" : {"$ne": ObjectId(str(row[0])) } }  )

		#MongoDB Connection
		ob_results = []
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["ozymandias"]
		mycol = mydb["ozys"]
		items.append( {"@type":"Movie"}  )
		for x in mycol.find({  "$and":  items  }).limit(100):
			ob_results.append( x )
		#return ob[0]
		#return render_template ('peliculas.html', len = len(ob_results), ob_results = ob_results, len_mx = len(ob_reco_mx), ob_reco_mx = ob_reco_mx)
		return render_template ('peliculasmongo.html', len = len(ob_results), ob_results = ob_results)
		#return jsonify(ob[0]["name"])
		#return str(ob_results[0]["_id"])
	else:

		return render_template('index.html')	

#VIDEOJUEGO
@app.route('/videojuego',methods=['GET','POST'])
def videojuego():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getvideojuego/' + id_vj ).text
			ob = json.JSONDecoder().decode(item)
			ob_results = ob["results"]
			return render_template ('vj.html', len = len(ob_results), ob_results = ob_results)
			#return "se realizo el get " + item

		else:

			return render_template('index.html')

#VIDEOJUEGOMONGO
@app.route('/videojuegomongo',methods=['GET','POST'])
def videojuegomongo():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			#MongoDB Connection
			ob_results = []
			myclient = pymongo.MongoClient("mongodb://localhost:27017/")
			mydb = myclient["ozymandias"]
			mycol = mydb["ozys"]
			for x in mycol.find({"_id":ObjectId(id_vj)}).limit(1):
				ob_results.append( x )
			return render_template ('vjmdb.html', len = len(ob_results), ob_results = ob_results)

		else:

			return render_template('index.html')

#LIBRO
@app.route('/libro',methods=['GET','POST'])
def libro():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getlibro/' + id_vj ).text
			ob = json.JSONDecoder().decode(item)
			ob_results = ob["results"]
			return render_template ('li.html', len = len(ob_results), ob_results = ob_results)
			#return "se realizo el get " + item

		else:

			return render_template('index.html')	

#LIBROMONGO
@app.route('/libromongo',methods=['GET','POST'])
def libromongo():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			#MongoDB Connection
			ob_results = []
			myclient = pymongo.MongoClient("mongodb://localhost:27017/")
			mydb = myclient["ozymandias"]
			mycol = mydb["ozys"]
			for x in mycol.find({"_id":ObjectId(id_vj)}).limit(1):
				ob_results.append( x )
			return render_template ('limdb.html', len = len(ob_results), ob_results = ob_results)

		else:

			return render_template('index.html')

#PELICULA
@app.route('/pelicula',methods=['GET','POST'])
def pelicula():
	if request.method == "GET":
		if 'session_name' in session:
			id_pe = request.args["id"]
			item = requests.get( 'http://ec2-18-191-242-247.us-east-2.compute.amazonaws.com/api/getpelicula/' + id_pe ).text
			ob = json.JSONDecoder().decode(item)
			ob_results = ob["results"]
			return render_template ('pe.html', len = len(ob_results), ob_results = ob_results)
			#return "se realizo el get " + item

		else:

			return render_template('index.html')	

#PELICULAMONGO
@app.route('/peliculamongo',methods=['GET','POST'])
def peliculamongo():
	if request.method == "GET":
		if 'session_name' in session:
			id_vj = request.args["id"]
			#MongoDB Connection
			ob_results = []
			myclient = pymongo.MongoClient("mongodb://localhost:27017/")
			mydb = myclient["ozymandias"]
			mycol = mydb["ozys"]
			for x in mycol.find({"_id":ObjectId(id_vj)}).limit(1):
				ob_results.append( x )
			return render_template ('pemdb.html', len = len(ob_results), ob_results = ob_results)

		else:

			return render_template('index.html')

#Logout
@app.route('/logout')
def logout():

	session.clear()

	return redirect(url_for('index'))			

if __name__ == "__main__":
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run(host='0.0.0.0',debug=True)
