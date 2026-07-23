from flask import Blueprint, jsonify, request

from api.extensions import db
from api.models import Calculation
from core import process_calculation

gauss_bp = Blueprint("gauss_bp", __name__, url_prefix="/api/calculations")

@gauss_bp.post("")
def create_calculation():
    data = request.get_json(silent=True) or {}

    required_fields = ["mean", "std_dev", "target_x"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        mean = float(data["mean"])
        std_dev = float(data["std_dev"])
        target_x = float(data["target_x"])
    except (TypeError, ValueError):
        return jsonify({"error": "mean, std_dev and target_x must be numbers."}), 400

    try: 
        result = process_calculation(mean, std_dev, target_x)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    new_calculation = Calculation(
        mean=mean,
        std_dev=std_dev,
        target_x=target_x,
        probability=result["probability"],
    )
    db.session.add(new_calculation)
    db.session.commit()

    response = new_calculation.to_dict()
    response["chart_base64"] = result["chart_base64"]
    return jsonify(response), 201


@gauss_bp.get("")
def list_calculations():
    calculations = Calculation.query.order_by(Calculation.created_at.desc()).all()
    return jsonify([c.to_dict() for c in calculations]), 200

@gauss_bp.get("/<int:calculation_id>")
def get_calculation(calculation_id: int):
    calculation = db.session.get(Calculation, calculation_id)
    if calculation is None:
        return jsonify({"error": "Calculation not found."}), 404

    result = process_calculation(calculation.mean, calculation.std_dev, calculation.target_x)
    response = calculation.to_dict()
    response["chart_base64"] = result["chart_base64"]
    return jsonify(response), 200

@gauss_bp.delete("/<int:calculation_id>")
def delete_calculation(calculation_id: int):
    calculation = db.session.get(Calculation, calculation_id)
    if calculation is None:
        return jsonify({"error": "Calculation not found."}), 404

    db.session.delete(calculation)
    db.session.commit()
    return jsonify({"message": f"Calculation {calculation_id} deleted sucessfully"}), 200