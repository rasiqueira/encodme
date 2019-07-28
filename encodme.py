# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 11:07:58 2019

@author: Rodrigo
"""

from flask import Flask, request, render_template, redirect, stream_with_context
from sqlite3 import OperationalError
import sqlite3
try:
    from urllib.parse import urlparse  # Python 3
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse  # Python 2
    str_encode = str
try:
    from string import ascii_lowercase
    from string import ascii_uppercase
except ImportError:
    from string import lowercase as ascii_lowercase
    from string import uppercase as ascii_uppercase
import base64
import hashlib
import io
from io import StringIO
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
import pandas as pd
from datetime import datetime

app = Flask(__name__)

host = 'localhost:5000'

def shorten_url(url):
   
    salt = "easycredito"

#    url = url.decode('utf-8')
    m = hashlib.md5()
    s = (url + salt).encode('utf-8')

    m.update(s)

    final_id = m.hexdigest()[-6:].replace('=', '').replace('/', '_')
    return(final_id)

def add_to_db(url):
   
    data = datetime.now()
    original_url = url
    shortened_url = shorten_url(original_url)
    
    try:
        with sqlite3.connect('url4.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                "INSERT INTO WEB_URL (ID, URL, data) VALUES (?, ?, ?)", 
                (shortened_url, original_url, data)
            )
            _lastrowid = (res.lastrowid)
    except:
        pass

    return(shortened_url)

def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID TEXT PRIMARY KEY,
        URL TEXT
        );
        """
    # Checks if table exists, else creates it    
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['u']
        if not url:
            return "URL não válida"
        
        def generate(url):
            encoded_string = add_to_db(url)
            print(encoded_string)
  
            
            return encoded_string
          
            
            
        encoded_string=generate(url)
                 
             
        return render_template('test.html', encoded_url=host+'/'+encoded_string, init=True)
    
    return render_template('test.html')


@app.route('/contador-de-cliques-da-url', methods=['GET', 'POST'])
def contador():
    if request.method == 'POST':
        url = request.form['u']
        if not url:
            return "URL não válida"
        def counter(url):
            ID = url[-6:]
            conn = sqlite3.connect('url4.db')
            #definindo um cursor
            cursor = conn.cursor()
            cursor.execute("""
                      SELECT clicked FROM WEB_URL
                      WHERE ID = (?)
                               """, (ID,))
            numero = cursor.fetchall()[0][0]

            if type(numero) is None:
                numero ='0'
            

            conn.close()
  
            
            return numero
          
            
            
        numero=counter(url)
                 
             
        return render_template('cliques.html', numero=numero)
        
        
    
    return render_template('cliques.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    if(len(short_url)==6):

        decoded = short_url
            
        url = '/'  # fallback if no URL is found
        conn = sqlite3.connect('url4.db')
        #definindo um cursor
        cursor = conn.cursor()
        cursor.execute("""
                      SELECT clicked FROM WEB_URL
                      WHERE ID = (?)
                               """, (decoded,))
        numero = cursor.fetchall()[0][0]

        if numero is None:
            numero = 1
        else:
            numero = int(numero)+1
        conn.close()
    
        conn = sqlite3.connect('url4.db')
        #definindo um cursor
        cursor = conn.cursor()
        cursor.execute("""
                      UPDATE WEB_URL set clicked = (?)
                      WHERE ID = (?)
                               """, (str(numero),decoded))
        conn.commit()
        conn.close()
        with sqlite3.connect('url4.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])
       
            try:
                short = res.fetchone()
                if short is not None:
                    url = short[0]
            except Exception as e:
                print(e)
        return redirect(url)
    else:
        return render_template('test.html')
       


if __name__ == '__main__':
    table_check()
    app.run(host='0.0.0.0', debug=True)