from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime

daily_bp = Blueprint("daily", __name__, url_prefix="/daily")