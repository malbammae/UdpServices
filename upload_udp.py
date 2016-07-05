from web import Alumnos,Bilioteca_udp
from crypto import *
from flask import jsonify
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime
import gridfs
import bson
from werkzeug.wsgi import wrap_file
import re
from werkzeug.routing import BaseConverter


url="http://files.udpcursos.com/"

upload={}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def run(app,request):
    @app.route('/upload', methods=['POST'])
    def upload_file():
        print "ACA"

        if request.method == 'POST':
            flowIdentifier = request.form['flowIdentifier']

            categoria=request.form['categoria']
            codigo=request.form['codigo']
            token=request.form['token']
            archivo=request.form['flowFilename']

            rut,passwd=decode_token(token)
            alumno=Alumnos.query.filter({'rut':rut}).first()
            if alumno == None:
                return "{}"


            current_chunk  = int(request.form["flowChunkNumber"])
            total_chunks   = int(request.form["flowTotalChunks"])

            file = request.files['file']
            filename = secure_filename(file.filename)

            if (os.path.exists('static/'+codigo))==False:
                os.makedirs('static/'+codigo)
            if (os.path.exists('static/'+codigo+"/"+categoria))==False:
                os.makedirs('static/'+codigo+"/"+categoria)

            if flowIdentifier not in upload:

                nombre=filename.split(".")
                nombre[len(nombre)-2]=nombre[len(nombre)-2]+"_"+str(random.getrandbits(5))
                nombre=".".join(nombre)
                upload[flowIdentifier]=nombre
                F = open(os.path.join('static/'+codigo+"/"+categoria, nombre), "wb")
            else:
                nombre = upload[flowIdentifier]
                F = open(os.path.join('static/'+codigo+"/"+categoria, nombre), "a")





            F.write(file.read())
            F.close()

            if current_chunk != total_chunks:
              return "{}"

            B=Bilioteca_udp()
            B.codigo=codigo
            B.identificador=flowIdentifier
            B.fecha=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            B.rut=alumno.rut
            B.responsable=alumno.full_name
            B.categoria=categoria
            B.archivo=archivo
            B.url=url+'static/'+codigo+"/"+categoria+"/"+nombre
            B.denuncias={}
            B.validar=1
            B.save()



            return jsonify(File=B.json())