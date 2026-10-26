from flask import Blueprint
from flask_login import login_required

index = Blueprint("index", __name__)

@index.route("/", methods=["GET"])
@login_required
def index_page():
    return ""
