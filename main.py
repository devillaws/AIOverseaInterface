import json
import flask
import openai
import openai_service
from flask import Flask, redirect, render_template, request, url_for, logging

app = Flask(__name__)


@app.route("/ai/openai/v1/gpt35turbo", methods=("GET", "POST"))
def gpt35turbo():
    return openai_service.gpt35turbo()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
