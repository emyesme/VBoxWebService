#!/usr/bin/python

import subprocess
from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)


#Ver la lista de máquinas virtuales en el host (VBoxManage list vms)
@app.route('/listarVBox', methods=['GET'])
def listarMaquinas():
	salida = subprocess.check_output(['vboxmanage', 'list' , 'vms'])
	lista_maquinas = salida.splitlines()
	return jsonify({'VBox': lista_maquinas})


#Ver la lista de máquinas en ejecución en el host (VBoxManage list runningvms)
@app.route('/listarVBoxEjecucion', methods=['GET'])
def corriendo():
	salida = subprocess.check_output(['vboxmanage', 'list' , 'runningvms'])
	lista_maquinas = salida.splitlines()
	return jsonify({'VBox': lista_maquinas})


#Dada una máquina virtual

#Ver sus características (VBoxManage showvminfo)
@app.route('/VBox/<string:vBox>', methods=['GET'])
def info(vBox):
	salida = subprocess.check_output(['vboxmanage', 'showvminfo', vBox ])
	lista_info = salida.splitlines()
	return jsonify({'VBox': lista_info})


#Ver la RAM asignada a la máquina virtual
@app.route('/VBox/ram/<string:vBox>', methods=['GET'])
def ram(vBox):
	vBox_info = subprocess.Popen(['vboxmanage', 'showvminfo', vBox ], stdout = subprocess.PIPE)
	salida = subprocess.Popen(['grep', 'Memory'], stdin = vBox_info.stdout, stdout = subprocess.PIPE)
	tercer_columna = subprocess.check_output(['awk', '{print $3}'], stdin=salida.stdout)
	memoria = tercer_columna.splitlines()
	return jsonify({'VBox': memoria})


#Ver el número de procesadores asignados a la máquina virtu
@app.route('/VBox/cpus/<string:vBox>', methods=['GET'])
def cpus(vBox):
	vBox_info = subprocess.Popen(['vboxmanage', 'showvminfo', vBox ], stdout = subprocess.PIPE)
	salida = subprocess.Popen(['grep', 'Number of CPUs'], stdin = vBox_info.stdout, stdout = subprocess.PIPE)
	cuarta_columna = subprocess.check_output(['awk', '{print $4}'], stdin=salida.stdout)
	cpus = cuarta_columna.splitlines()
	return jsonify({'VBox': cpus})


#Brindar el número de tarjetas de red conectadas a una máquina virtual
@app.route('/VBox/nic/<string:vBox>', methods=['GET'])
def nic(vBox):
	vBox_info = subprocess.Popen(['vboxmanage', 'showvminfo', vBox ], stdout = subprocess.PIPE)
	controladores_red = subprocess.Popen(['grep', 'NIC'], stdin = vBox_info.stdout, stdout = subprocess.PIPE)
	mac = subprocess.Popen(['grep', 'MAC'], stdin = controladores_red.stdout, stdout = subprocess.PIPE)
	salida = subprocess.check_output(['wc', '-l'], stdin = mac.stdout)
	numero_tarjetas = salida.splitlines()
	return jsonify({'VBox': numero_tarjetas})


#Modificar el número de CPUs
@app.route('/VBox/modificarCpus/<string:vBox>/<string:cpu>', methods=['GET'])
def modificarCpus(vBox, cpu):
	subprocess.run(['vboxmanage', 'modifyvm', vBox, '--cpus' , cpu ])
	return jsonify ({'VBox': "Si la maquina no se encontraba corriendo se modifico el número de CPUs en la maquina virtual: " + vBox + " a " + cpu})

#Modificar la RAM asignada a la máquina virtual
@app.route('/VBox/modificarRam/<string:vBox>/<string:ram>', methods=['GET'])
def modificarRam(vBox, ram):
	subprocess.run(['vboxmanage', 'modifyvm', vBox, '--memory' , ram ])
	return jsonify ({'VBox': "Si la maquina no se encontraba corriendo se modifico la RAM asignada en la maquina virtual: " + vBox + " a " + ram + "MB"})

#Modificar la cantidad de porcentaje del procesador que se le asigna a una máquina virtual
@app.route('/VBox/modificarPorcentajeCpu/<string:vBox>/<string:porcentaje>', methods=['GET'])
def modificarPorcentajeCpu(vBox, porcentaje):
	if(int(porcentaje)>0 and int(porcentaje)<=100):
		subprocess.run(['vboxmanage', 'modifyvm', vBox, '--cpuexecutioncap' , porcentaje ])
		return jsonify ({'VBox': "Si la maquina no se encontraba corriendo se modifico el porcentaje del procesador que se asigna a la maquina: " + vBox + " a " + porcentaje + "%"})
	else:
		return jsonify ({'VBox': "No se modifico el porcentaje del procesador, debe asignarse un porcentaje entre cero y cien"})


@app.errorhandler(404)
def not_found(error):
 return make_response(jsonify({'error': 'No encontrado'}), 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port = 5000)
