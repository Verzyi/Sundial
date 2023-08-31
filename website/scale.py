from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import math
import matplotlib.pyplot as plt







scale = Blueprint('scale', __name__)

def calculate_new_scale(actual_values, input_values, offset):
    slope = 1.0 / np.mean(input_values)
    new_scale = (actual_values - offset) * slope
    return new_scale

@scale.route('/scale', methods=['GET', 'POST'])
@login_required
def index():
    x_actual=0 
    x_input=0
    y_actual=0 
    y_input=0
    
    nominal_values = [0.5, 0.5, 1.5, 1.5, 2.5, 2.5, 3.5, 3.5, 4.5, 4.5, 5.5, 0.5, 0.5, 1.5, 1.5, 2.5, 2.5, 3.5]
    
    if request.method == 'POST':
        x_actual = np.array(request.form.getlist('x_actual'), dtype=float)
        x_input = np.array(request.form.getlist('x_input'), dtype=float)
        y_actual = np.array(request.form.getlist('y_actual'), dtype=float)
        y_input = np.array(request.form.getlist('y_input'), dtype=float)
        offset = float(request.form['offset'])

        x_new_scale = calculate_new_scale(x_actual, x_input, offset)
        y_new_scale = calculate_new_scale(y_actual, y_input, offset)

        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.scatter(x_actual, x_new_scale, label='X Data')
        plt.xlabel('Actual')
        plt.ylabel('New Scale')
        plt.title('X Data vs New Scale')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.scatter(y_actual, y_new_scale, label='Y Data', color='orange')
        plt.xlabel('Actual')
        plt.ylabel('New Scale')
        plt.title('Y Data vs New Scale')
        plt.legend()

        plt.tight_layout()

        plot_path = 'static/plot.png'  # Save the plot image
        plt.savefig(plot_path)
        plt.close()

        return render_template('scale.html', plot_path=plot_path, user=current_user)

    return render_template('scale.html',user=current_user,nominal_values=nominal_values)