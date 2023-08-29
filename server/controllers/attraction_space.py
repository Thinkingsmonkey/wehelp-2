from flask_restx import Resource, Namespace, reqparse
from ..extensions import db
from ..models.db_models import Attraction, AttractionImg
from ..models.api_models import *
from sqlalchemy import func

attraction_space = Namespace(path="/api",name="旅遊景點")

@attraction_space.route("/acttractions")
@attraction_space.doc(description="取得不同分頁的旅遊景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選")
# @attraction_space.response() # 準備回應格式
class ActtractionsAPI(Resource):

    # query string swagger 說明用
    parser = attraction_space.parser()
    parser.add_argument("page", type=int, required=True, location="args")
    parser.add_argument("keyword", type=str, location="args")
    # 設定 參數的說明，參數名需相同
    @attraction_space.doc(params={"page": "要取得的分頁，每頁 12 筆資料", "keyword": "用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選"}) 
    # mask=None 關掉 X-field 預設(輸出 marshal 才可用)
    @attraction_space.marshal_list_with(attractions_output_model, mask=None) 
    @attraction_space.expect(parser)
    def get(self):
        # query string API 執行用
        parser = reqparse.RequestParser()
        parser.add_argument("page", type=int, required=True, location="args")
        parser.add_argument("keyword", type=str, location="args")
        args = parser.parse_args()

        # 取得參數
        page = args["page"]
        keyword = args["keyword"]
        # error handle
        if page > 5 or page < 0:
            attraction_space.abort(400, "page is not validation")

        if "台" in keyword:
            print("台")
        if "臺" in keyword:
            print("臺")

        keyword_attractions = Attraction.query.filter(Attraction.name.ilike(f'%台%')).all()
        keyword_attractions1 = Attraction.query.filter(Attraction.name.ilike(f'%臺%')).all()

        print(len(keyword_attractions)+ len(keyword_attractions1))

        # 搜索 MRT 為 keyword 的站
        keyword_attraction = Attraction.query.filter_by(MRT=keyword).first()
        if keyword_attraction:
            # 若符合找出所有捷運站景點
            keyword_attractions = Attraction.query.filter(MRT=keyword)
        else:
            # 若不符合，使用模糊搜索找所有景點
            keyword_attractions = Attraction.query.filter(Attraction.name.ilike(f'%{keyword}%'))
        # 依條件搜尋資料
        items_per_page = 12
        attractions = keyword_attractions.paginate(page=page, per_page=items_per_page, error_out=False)
        imgs = AttractionImg.query.all()

        # 輸出轉換
        data_list = []
        for attraction in attractions:
            attraction_info = {}
            attraction_info["id"] = attraction._id
            attraction_info["name"] = attraction.name
            attraction_info["category"] = attraction.CAT
            attraction_info["description"] = attraction.description
            attraction_info["address"] = attraction.address
            attraction_info["transport"] = attraction.direction
            attraction_info["mrt"] = attraction.MRT
            attraction_info["lat"] = attraction.latitude
            attraction_info["lng"] = attraction.longitude
            data_list.append(attraction_info)
        # images 輸出轉換
        for data in data_list:
            data["images"] = []
            for img in imgs:
                if data["id"] == img.attraction_id:
                    data["images"].append(img.img)
        return {
            "nextPage":attractions.next_num,
            "data": data_list
        }, 200