from flask_restx import Resource, Namespace
from ..extensions import db
from ..models.db_models import Attraction, AttractionImg
from ..models.api_models import *

acttraction_space = Namespace("api/")

@acttraction_space.route("/acttractions")
class ActtractionsAPI(Resource):
    
    # @acttraction_space.marshal_with(attractions_output_model)
    @acttraction_space.expect(acttractions_input_model)
    def post(self):
        return {"ok": True}, 200