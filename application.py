from operator import and_
from flask import Flask, jsonify, request
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
import pandas as pd
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re

application = Flask(__name__)
nltk.download('stopwords')
vectorization = joblib.load('./vectorizer.pkl')
svm_model = joblib.load('./newsModel.pkl')

def fake_news_detection(news):
    input_data = {"text":[news]}
    new_def_test = pd.DataFrame(input_data)
    new_def_test["text"] = new_def_test["text"].apply(wordopt)
    new_x_test = new_def_test["text"]
    vectorized_input_data = vectorization.transform(new_x_test)
    prediction = svm_model.predict(vectorized_input_data)

    if(prediction == [1]):
        return 'Real News'
    else:
        return 'Fake News'



DB_URI = "mysql+pymysql://admin:pFRQT725&yX1Ytj7@aa11x33816hc477.cko51fghichq.us-east-2.rds.amazonaws.com/ebdb"
application.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    prediction = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<History %r>' % self.news


db.create_all()


def my_random_string(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-", "")
    return random[0:string_length]

ps = PorterStemmer()
def wordopt(text):
    text = re.sub('[^a-zA-Z]', ' ',text)
    text = text.lower()
    text = text.split()
    text = [ps.stem(word) for word in text if not word in stopwords.words('english')]
    text = ' '.join(text)
    return text


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/api/v1/login',methods=['POST'])
def login():

    try:
        email = request.form['email']
        password = request.form['password']
        user = db.session.query(User).filter(and_(User.email == email,User.password == password)
                                          ).first()

        if(user == None):
            return jsonify(
            status=401,
            data='Invalid Credentials'
            )

        return jsonify(
            status=201,
            data=user.id
        )

    except Exception as e:
        return jsonify(
            status=409,
            msg=e
        )


@application.route('/api/v1/register',methods=['POST'])
def register():
    try:

        email = request.form['email']
        password = request.form['password']
        print(email,password)
        reg = User(email=email, password=password)
        db.session.add(reg)
        db.session.commit()
        user = db.session.query(User).filter(and_(User.email == email,User.password == password)
                                          ).first()
        return jsonify(
            status=201,
            data=user.id
        )
    except Exception as e:
        print(e)
        return jsonify(
            status=409,
            msg="user already exits!"
        )


@application.route('/api/v1/predict', methods=['POST'])
def news_status():


    try:
        # real news
        # pre = fake_news_detection('The White House said on Friday it was set to kick off talks next week with Republican and Democratic congressional leaders on immigration policy, government spending and other issues that need to be wrapped up early in the new year. The expected flurry of legislative activity comes as Republicans and Democrats begin to set the stage for midterm congressional elections in November. President Donald Trumpâ€™s Republican Party is eager to maintain control of Congress while Democrats look for openings to wrest seats away in the Senate and the House of Representatives. On Wednesday, Trumpâ€™s budget chief Mick Mulvaney and legislative affairs director Marc Short will meet with Senate Majority Leader Mitch McConnell and House Speaker Paul Ryan - both Republicans - and their Democratic counterparts, Senator Chuck Schumer and Representative Nancy Pelosi, the White House said. That will be followed up with a weekend of strategy sessions for Trump, McConnell and Ryan on Jan. 6 and 7 at the Camp David presidential retreat in Maryland, according to the White House. The Senate returns to work on Jan. 3 and the House on Jan. 8. Congress passed a short-term government funding bill last week before taking its Christmas break, but needs to come to an agreement on defense spending and various domestic programs by Jan. 19, or the government will shut down. Also on the agenda for lawmakers is disaster aid for people hit by hurricanes in Puerto Rico, Texas and Florida, and by wildfires in California. The House passed an $81 billion package in December, which the Senate did not take up. The White House has asked for a smaller figure, $44 billion. Deadlines also loom for soon-to-expire protections for young adult immigrants')
        # pre = fake_news_detection(' A federal judge in New York on Thursday threw out a lawsuit that had accused President Donald Trump of violating the U.S. Constitution by accepting foreign payments through his hotels and other businesses, handing him a major victory on an issue that has dogged him since even before he took office in January. Though other lawsuits remain pending that make similar claims, the ruling by U.S. District Judge George Daniels is the first to weigh the merits of the U.S. Constitutionâ€™s anti-corruption provisions as they apply to Trump, a wealthy businessman who as president regularly visits his own hotels, resorts and golf clubs. In a 29-page opinion granting the Trump administrationâ€™s request to toss the suit, Daniels said the plaintiffs did not have legal standing to bring the suit. The plaintiffs included the nonprofit watchdog group Citizens for Responsibility and Ethics in Washington (CREW), a hotel owner, a hotel events booker and a restaurant trade group. The lawsuit, filed after the Republican president took office in January, accused Trump of running afoul of the Constitutionâ€™s â€œemolumentsâ€ clause by maintaining ownership of his business empire while in office.  The emoluments clause, designed to prevent corruption and foreign influence, bars U.S. officials from accepting gifts from foreign governments without congressional approval. Trump has ceded day-to-day control of his businesses to his sons. Critics have said that is not a sufficient safeguard. The plaintiffs said they are legally injured when foreign governments try to â€œcurry favorâ€ with Trump by paying to use his businesses, such as the Trump International Hotel in Washington or a high-end restaurant at a Trump hotel in New York City. The plaintiffs said this leads them to have lost patronage, wages and commissions. U.S. Department of Justice spokeswoman Lauren Ehrsam said the Trump administration â€œappreciates the courtâ€™s ruling.â€ Daniels, appointed to the bench by Democratic former President Bill Clinton, said in his decision that the plaintiffsâ€™ claims were speculative. Daniels said Trump had amassed wealth and fame even before taking office and was competing in the hospitality industry.  â€œIt is only natural that interest in his properties has generally increased since he became president,â€ the judge wrote. The judge also said that if Congress wanted to do something about the presidentâ€™s actions, it could. â€œCongress is not a potted plant,â€ Daniels said. â€œIt is a co-equal branch of the federal government with the power to act.â€ CREW Executive Director Noah Bookbinder said that his legal team is weighing options on how to proceed. â€œWhile todayâ€™s ruling is a setback, we will not walk away from this serious and ongoing constitutional violation,â€ Bookbinder added. Some legal experts had raised concerns even before his inauguration on Jan. 20 that Trump would violate the emoluments clause as president.')

        # fake news
        # pre = fake_news_detection('Republicans have had seven years to come up with a viable replacement for Obamacare but they failed miserably. After taking a victory lap for gifting the wealthy with a tax break on Wednesday, Donald Trump looked at the cameras and said,  We have essentially repealed Obamacare and we will come up with something that will be much better. Obamacare has been repealed in this bill,  he added. Well, like most things Trump says, that s just not true. But, if the former reality show star could have done that in order to eradicate former President Obama s signature legislation, he would have and without offering an alternative.Senate Majority Leader Mitch McConnell told NPR that  This has not been a very bipartisan year. I hope in the new year, we re going to pivot here and become more cooperative. An Obamacare repeal in 2018 is DOA. Well, we obviously were unable to completely repeal and replace with a 52-48 Senate,  the Kentucky Republican said.  We ll have to take a look at what that looks like with a 51-49 Senate. But I think we ll probably move on to other issues. NPR reports:McConnell hopes to focus instead on stabilizing the insurance marketplaces to keep premiums from skyrocketing in the early months of 2018, a promise he made to moderate Republican Sen. Susan Collins of Maine to get her support for the tax bill.On top of that McConnell broke with House Speaker Paul Ryan, R-Wis., on the approach to paring back spending on programs like Medicaid and food stamps. McConnell told NPR he is  not interested  in using Senate budget rules to allow Republicans to cut entitlements without consultation with Democrats. I think entitlement changes, to be sustained, almost always have to be bipartisan,  McConnell said.  The House may have a different agenda. If our Democratic friends in the Senate want to join us to tackle any kind of entitlement reform. I d be happy to take a look at it. This is coming from Mitch McConnell. He knows Donald Trump is destroying the GOP. It doesn t matter, Sen. McConnell. We still recall him saying that his  number one priority is making sure president Obama s a one-term president. Well, we re hoping that Trump doesn t last a full term. Funny how that works.Photo by Chip Somodevilla/Getty Images')
        # d = pd.Series(pre).to_json(orient='values')


        data = request.form['news']
        user_id = request.form['user_id']

        user = db.session.query(User).get(user_id)
        if(user == None):
            return jsonify(
            status=401,
            data='Invalid Credentials'
            )

        status = fake_news_detection(data)
        reg = History(news = data,user_id = user_id,prediction=status)
        db.session.add(reg)
        db.session.commit()
        return jsonify(
        data=status
        )
    except Exception as e:
        print(e)
        return jsonify(
            status=409,
            msg=e
        )


if __name__ == '__main__':
    application.run(debug=True)
