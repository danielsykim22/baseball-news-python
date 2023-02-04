from datetime import datetime
from time import sleep, time
from xml.dom.minidom import Element
from flask import Flask, render_template, request
import chromedriver_autoinstaller as auto
from bs4 import BeautifulSoup as bs
from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

url = "https://"
color = "<strong style='color:{0};'>{1}</strong>"

def obj_to_text(selector: str, soup: Element):
    return [s.text for s in soup.select(selector)]


def obj_to_float(selector: str, soup: Element):
    return [int(float(s.text)) for s in soup.select(selector)]


auto.install()
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

def list_player(player_id):
    result2 = []
    print("데이터 수집중...")
    driver.get(
        f"https://m.sports.naver.com/player/index?category=kbo&tab=record&from=sports&playerId={player_id}")
    sleep(1)
    inner = driver.page_source
    soup = bs(inner, "html.parser")

    print("최근 연도 조회중...")
    driver.get(
        f"https://sports.news.naver.com/kbaseball/record/index?category=kbo&year={datetime.now().year}")
    sleep(1)
    inner2 = driver.page_source

    soup2 = bs(inner2, "html.parser")
    game = obj_to_float(
        "#regularTeamRecordList_table tr td:nth-child(3)", soup2)
    avg = sum(game)/len(game)
    # a=soup.select("#_careerStatsTable > tbody > tr:nth-child(2) > td:nth-child(1)")
    # result += "타율:", a)
    player = obj_to_text("#_title_area > h2", soup)
    player_name = player[0].split(" NO.")[0]
    team = soup.select_one("#_title_area > span > em:nth-child(1)").text
    head = obj_to_text("#_careerStatsTable th", soup)
    head1 = ["AVG", "OBA", "SLG", "OPS"]
    body = soup.select("#_careerStatsTable > tbody > tr")
    # 0:타율 1:경기수 2:타수 3:안타 4:2루타 5:3루타 6:홈런 7:타점 8:득점 9:도루 10:볼넷 11:삼진 12:출루율 13:장타율 14:OPS 20:WAR

    body = [[(float(b.text) if '.' in b.text else int(b.text)) if b.text != '-' else None for b in bo.select("td")]
            for bo in body]
    atk_rate, amount_of_game, amount_of_hit, hit, nd, th, homerun, hit_point, point, steel, walk, str_out, out_rate, jangta, OPS, WAR = body[
        1][:15] + body[1][20:]
    body1 = [atk_rate, out_rate, jangta, OPS]
    result2.append("<div style='font-size: 200%;'>")
    result2.append(f"{team} {player_name}은(는) 2022 시즌 {datetime.now().strftime('%m월 %d일')} 기준 {amount_of_game:d}경기 {amount_of_hit:d}타수 {hit:d}안타 {homerun:d}홈런 {hit_point:d}타점 타율 {atk_rate:.3f} 출루율 {out_rate:.3f} 장타율 {jangta:.3f} OPS {OPS:.3f}을 기록했다. ")
    score = 0
    if amount_of_game/avg >= 0.9:
        result2.append(color.format("blue", "올 시즌 경기에 꾸준히 출전하고 있고, "))
        score += 0.5
    elif 0.9 > amount_of_game/avg >= 0.8:
        result2.append(color.format("turquoise","올 시즌 경기에 꾸준히 출전하고 있고, "))
        score += 0.25
    elif 0.8 > amount_of_game/avg >= 0.7:
        result2.append(color.format("green","올 시즌 출전한 경기수는 보통 수준이고, "))
    elif 0.7 > amount_of_game/avg >= 0.6:
        result2.append(color.format("yellow","올 시즌 출전한 경기수는 보통 수준이고, "))
    elif 0.6 > amount_of_game/avg >= 0.5:
        result2.append(color.format("orange","올 시즌 경기에 꾸준히 출전하지 못하고 있고, "))
        score -= 0.25
    elif amount_of_game/avg <= 0.5:
        result2.append(color.format("red","올 시즌 경기에 꾸준히 출전하지 못하고 있고, "))
        score -= 0.5

    if atk_rate >= 0.320:
        result2.append(color.format("blue","타율만 보면 엄청난 활약을 보이고 있다. "))
        score += 1.5
    elif 0.290 <= atk_rate < 0.320:
        result2.append(color.format("turquoise","타율만 보면 준수한 성적을 기록하고 있다.  "))
        score += 0.9
    elif 0.260 <= atk_rate < 0.290:
        if atk_rate>=0.275:
            result2.append(color.format("green","타율만 보면 평범한 성적을 기록하고 있다.  "))
            score+=0.3
        else:
            result2.append(color.format("yellow","타율만 보면 평범한 성적을 기록하고 있다.  "))
            score-=0.3
    elif 0.230 <= atk_rate < 0.260:
        result2.append(color.format("orange","타율만 보면 아쉬운 성적을 기록하고 있다.  "))
        score -= 0.9
    else:
        result2.append(color.format("red","타율만 보면 크게 부진하고 있다.  "))
        score -= 1.5
    if jangta >= 0.500:
        result2.append(color.format("blue","장타율은 높은 편으로 파워가 좋아서 장타 생산력이 매우 뛰어나다."))
        score += 0.75
    elif 0.450 <= jangta < 0.500:
        result2.append(color.format("turquoise","장타율은 높은 편으로 장타를 많이 치는 편이다."))
        score += 0.45
    elif 0.380 <= jangta < 0.450:
        if jangta >= 0.415:
            result2.append(color.format("green","장타율은 보통 수준으로 장타를 많이 치지는 못하지만 어느 정도 파워가 있다."))
            score += 0.15  
        else:
            result2.append(color.format("yellow","장타율은 보통 수준으로 장타를 많이 치지는 못하지만 어느 정도 파워가 있다."))
            score -= 0.15
    elif 0.330 <= jangta < 0.380:
        result2.append(color.format("orange","장타율은 낮은 편으로 장타를 많이 치지 못한다."))
        score -= 0.45
    else:
        result2.append(color.format("red","장타율은 낮은 편으로 파워가 부족해서 장타 생산력이 많이 부족하다."))
        score -= 0.75
    if out_rate >= 0.400:
        result2.append(color.format("blue","출루율은 아주 높은 편으로 타율과 선구안이 좋아 출루능력이 엄청나다. "))
        score += 1
    elif 0.370 <= out_rate < 0.400:
        result2.append(color.format("turquoise","출루율은 높은 수준으로 타율과 선구안이 좋아 출루를 많이 하는 편이다."))
        score += 0.6
    elif 0.350 <= out_rate < 0.370:
        result2.append(color.format("green","출루율은 보통 수준으로 출루를 많이 하지는 못하지만 어느 정도의 안타 생산력과 선구안이 있다. "))
        score += 0.2
    elif 0.330 <= out_rate < 0.350:
        result2.append(color.format("yellow","출루율은 보통 수준으로 출루를 많이 하지는 못하지만 어느 정도의 안타 생산력과 선구안이 있다. "))
        score -= 0.2
    elif 0.300 <= out_rate < 0.330:
        result2.append(color.format("orange","출루율은 낮은 수준으로 타율과 선구안이 안좋아 출루를 많이 하지 못하는 편이다."))
        score -= 0.6
    else:
        result2.append(color.format("red","출루율은 아주 낮은 수준으로 타율과 선구안이 안좋아 출루능력이 많이 떨어진다. "))
        score -= 1
    if hit_point/amount_of_hit >= 0.185 or hit_point>=100:
        result2.append(color.format("blue","타점이 많아 타점 생산력이 뛰어나다."))
        score += 0.75
    elif hit_point/amount_of_hit <= 0.11:
        result2.append(color.format("red","타점이 적어 타점 생산력이 부족하다."))
        score -= 0.75
    if homerun/amount_of_hit >= 0.045:
        result2.append(color.format("blue",f"시즌 {homerun}홈런으로 홈런도 아주 많이 치고 있다. "))
        score += 1
    elif 0.034 <= homerun/amount_of_hit < 0.045:
        result2.append(color.format("turquoise",f"시즌 {homerun}홈런으로 홈런을 많이 치고 있다. "))
        score += 0.5
    elif 0.023 <= homerun/amount_of_hit < 0.034:
        if homerun/amount_of_hit>=0.0285:
            result2.append(color.format("green",f"시즌 {homerun}홈런으로 홈런은 보통 수준으로 치고 있다. "))
            score+=0.25
        else:
            result2.append(color.format("yellow",f"시즌 {homerun}홈런으로 홈런은 보통 수준으로 치고 있다. "))
            score-=0.25
    elif 0.012 <= homerun/amount_of_hit < 0.023:
        result2.append(color.format("orange",f"시즌 {homerun}홈런으로 홈런을 많이 치지 못하고 있다. "))
        score -= 0.5
    else:
        result2.append(color.format("red",f"시즌 {homerun}홈런으로 홈런도 거의 치지 못하고 있다. "))
        score -= 1
    if walk >= str_out:
        result2.append(color.format("blue","볼넷 수가 삼진 수 이상으로 선구안이 매우 뛰어나다. "))
        score += 0.5
    elif walk*3 <= str_out:
        result2.append(color.format("red","선구안이 매우 떨어진다. "))
        score -= 0.5
    if steel/amount_of_game >= 0.17:
        result2.append(color.format("blue",f"시즌 {int(steel)}도루로 도루를 많이 하고 주력이 매우 빠르다."))
        score += 0.5
    elif steel/amount_of_game <= 0.023:
        result2.append(color.format("red","도루가 거의 없어 주력이 매우 느리거나 도루를 잘 하지 않는다."))
        score -= 0.25
    game_log = soup.select("#_gameLogTable tr")[1:]
    game_log = [obj_to_float("td", s)[1:3] for s in game_log]
    s1 = sum([g[0] for g in game_log])
    s2 = sum([g[1] for g in game_log])
    if s2==0:
        if WAR >= 5.3:
            result2.append(color.format("blue",f"올 시즌 WAR(승리기여도)은 {WAR}이다. "))
            score += 0.5
        elif 4 <= WAR < 5.3:
            result2.append(color.format("turquoise",f"올 시즌 WAR(승리기여도)은 {WAR}이다. "))
            score += 0.3
        elif 3 <= WAR < 4:
            result2.append(color.format("green",f"올 시즌 WAR(승리기여도)은 {WAR}이다. "))
            score += 0.1
        elif 2.3 <= WAR < 3:
            result2.append(color.format("yellow",f"올 시즌 WAR(승리기여도)은 {WAR}이다. "))
            score -= 0.1
        elif 1.5 <= WAR < 3:
            result2.append(color.format("orange",f"올 시즌 WAR(승리기여도)은 {WAR}이다. "))
            score -= 0.3
        else:
            result2.append(color.format("red",f"올 시즌 WAR(승리기여도)은 {WAR}이다. "))
            score -= 0.5
    else:
        result2.append(f"올 시즌 WAR(승리기여도)은 {WAR}이다. ")
    # _gameLogTitleList
    a=0
    if s2 == 0:
        a=1
    if a==0:
        if s2/s1 >= atk_rate*1.25 and s2/s1!=0:
            result2.append(color.format("blue",f"최근 10경기 타율 {s2/s1:.3f}로 타격감이 뜨겁다.\n"))
        elif s2/s1 <= atk_rate*0.75 and atk_rate!=0:
            result2.append(color.format("red",f"최근 10경기 타율 {s2/s1:.3f}로 타격감이 떨어지고 있다.\n"))
    result2.append("<br></>")
    if score >= 5.5:
        result2.append(color.format("blue",f"올해 성적 총평으로는 리그를 지배하는 수준이다.<br>올해 총점: {score+6.75}/13.75({(score+6.75)/13.75*100:.2f}%)</br>"))
    elif 3 <= score < 5.5:
        result2.append(color.format("turquoise",f"올해 성적 총평으로는 엄청난 활약을 보여주고 있다.<br>올해 총점: {score+6.75}/13.75({(score+6.75)/13.75*100:.2f}%)</br>"))
    elif 0 <= score < 3:
        result2.append(color.format("green",f"올해 성적 총평으로는 기대 이상의 준수한 활약을 하고 있다.<br>올해 총점: {score+6.75}/13.75({(score+6.75)/13.75*100:.2f}%)</br>"))
    elif -3 <= score < 0:
        result2.append(color.format("yellow",f"올해 성적 총평으로는 기대 이하의 아쉬운 성적을 내고 있다.<br>올해 총점: {score+6.75}/13.75({(score+6.75)/13.75*100:.2f}%)</br>"))
    elif -5.5 <= score < -3:
        result2.append(color.format("orange",f"올해 성적 총평으로는 많이 부진하고 있어 반전이 필요해 보인다.<br>올해 총점: {score+6.75}/13.75({(score+6.75)/13.75*100:.2f}%)</br>"))
    else:
        result2.append(color.format("red",f"그냥 답이 없다.<br>올해 총점: {score+6.75}/13.75({(score+6.75)/13.75*100:.2f}%)</br>"))
    result2.append("통산 기록<br>")
    result2.append("<table>")
    result2.append("<tr>")
    season = obj_to_text("#_careerStatsTitleList",soup)[0].split("\n")[1:-1]
    s_dict = {}
    record = ["시즌", "타율", "경기수", "타수", "안타", "2루타", "3루타", "홈런", "타점", "득점", "도루", "볼넷", "삼진", "출루율", "장타율", "OPS", "IsoP", "BAPIP", "wOBA", "wRC", "WPA", "WAR"]
    for rec in record:
        result2.append(f"<th>{rec}")
    for i, s in enumerate(season):  
        s_dict[s] = body[i]
    result2.append("</tr>")
    j=0
    for k, v in s_dict.items():
        result2.append("<tr>")
        result2.append(f"<td>{season[j]}")
        for x in v:
            result2.append(f"<td>{x if x or x==0 else '-'}</td>")
        result2.append("</tr>")
        j=j+1
    result2.append("</table>")
    result2.append("</div>")
    return result2
app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template("index.html")

@app.route("/result")
def search():
    string:str = request.args.get("pid")
    if not string.isdigit():
        data = requests.get(f"https://ac.sports.naver.com/ac/player/kbo?&q_enc=UTF-8&st=1&r_lt=1&frm=search&r_format=json&r_enc=UTF-8&t_koreng=1&q={string}&_=1673074580608")
        data = data.json()['items'][0][0][1][0]
        string = data
    return render_template("result.html", data="\n".join(list_player(string)))

if __name__ == "__main__":
    app.run("0.0.0.0", port=80)
driver.close()
