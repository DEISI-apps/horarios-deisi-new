from horarios.models import *


alunos = "adelciamiguel@gmail.com , afonsoquartau828@gmail.com , alcantranetomanuel@gmail.com , aldairamaralaldair@gmail.com , ale.sg.oliveira@gmail.com , alexandra.campos@ulusofona.pt, alexlukeny12@gmail.com , amc3@outlook.pt , alexferreiragodinho@gmail.com , f4849@ulusofona.pt, anactividade.moises@gmail.com , andreafonsofarinha@gmail.com , grandejugador28@gmail.com , andremartires@outlook.com , ahrs1998@outlook.com, andrecunhavieira@gmail.com , yukiterupotato@gmail.com , andrepan327@gmail.com , antonio.gab003@gmail.com , auriacagigal32@gmail.com , abelanderson129@gmail.com , bernardoayres2001@gmail.com , ebernardojspa@gmail.com , bemiguelalvespinheiro@gmail.com , bernardoramalhete2000@gmail.com, brunoalexsn@gmail.com , bruno.martinho.2000@gmail.com , carlenecarvalho32@gmail.com , carlosraul2018@hotmail.com , chelciabarroso9@gmail.com , daniel.peralta@live.u-tad.com , daniel.ivancenco@gmail.com , davidalexandre52006@gmail.com , delcioicones@gmail.com , denivaldomarcio0@gmail.com , diogofonseca.x@gmail.com , diogofilipepardal@gmail.com , diogo560filipe@gmail.com , diogolalves2006@gmail.com , diogocorreia561@gmail.com , diogomanueloliveira1@gmail.com , diogo2005santosnunes@gmail.com , domingosmuandajunior07@gmail.com , duartegoulao06@gmail.com , fernandesnduarte@gmail.com , duarte05_04@hotmail.com , eliastenente05@gmail.com , terciobarrvs@gmail.com , emersoneff2003@gmail.com , estherutazi38@gmail.com , evandrozaborowski@gmail.com , zfelkmacedoz@gmail.com , filipecondeca6@gmail.com , filipemiguel1234@gmail.com , filpetolentino@gmail.com , francisco.albuquerque2007@gmail.com , franciscomaria.valente@gmail.com , fmcantomoreira@gmail.com , franciscoxavierpearson@gmail.com , geraldosambo4@gmail.com , gilbertopingi@gmail.com , 1412goncalocandeias@gmail.com , goncalopina2903@gmail.com , guga.santos.neves@gmail.com , acdlribeiro@gmail.com , guialves20@gmail.com , guilherme.gfrantz@gmail.com , guisacoelho2006@gmail.com , guiqcoelho@hotmail.com , istoeparaasteam@gmail.com , hcalado23@gmail.com , hugo4lex2004@gmail.com , hugo.miguxl@gmail.com , jaimemloran@gmail.com , janioklalmeida05@gmail.com , jasovarela000@gmail.com , carloneves95@gmail.com , joaofilipemiguel2005@gmail.com , joao.f.acad@icloud.com , johny.mart009@gmail.com , joaoribeirofrutuoso@gmail.com , jonhsoncandumba@gmail.com , josejosejose2348@gmail.com , joseruisoares23@gmail.com , juliojuliohilario10@gmail.com , silvangelkadi@gmail.com , kauemartins3@icloud.com , kelvincosta0707@gmail.com , elsiocoimbra@gmail.com , letiziafbonunes@icloud.com , kleocreis@gmail.com , levisebastiao59@gmail.com , alveslily330@gmail.com , lumberbim@gmail.com , aaalberto616@gmail.com , l_botelho@hotmail.com , lucasmiguelcostamoura@gmail.com , lucio.studer@gmail.com, lucio.studer@ulusofona.pt, luilsonpereira12@gmail.com , luiscdcampos@gmail.com , luiscdcampos@gmail.com , manuell.albizu@gmail.com , manuelafonso2004@gmail.com , marcoscarvalho90@gmail.com , martimwilsonescola@gmail.com , martimsoaresrodrigues4@gmail.com , mpmarques322@gmail.com , miguel.csilvamorgado@gmail.com , moisesanderson450@gmail.com , nelson10almeida@outlook.pt , noahobadia11@gmail.com , efrahimtks@gmail.com , nunotainha@gmail.com , alexei.tolkunov@gmail.com , orlandopucuta14@gmail.com , pguimas2305@gmail.com , baratta.paullo@gmail.com , paulobalduino88@gmail.com , pedro_s9@outlook.com , pedrorsouza2006@gmail.com , rafabarafa@gmail.com , rafaelgomessantos2006@gmail.com , user.jogos.rafa@gmail.com , rafafootcanal97@gmail.com , kikors21@gmail.com , ricardopereiraa2004@gmail.com , freirolas@gmail.com , ricardofigueiredo30012007@gmail.com , ricostalopes@gmail.com , ricardontsantos03@gmail.com , ricardobacalhau62@gmail.com , rb102004@gmail.com , rodrigosantos374@outlook.pt , rodrigomarque123@gmail.com , rodrigotuga96@gmail.com , rodrigo.silva.vale@gmail.com , ruangomes.back@gmail.com , rx3mafia1@gmail.com , rui.moreira619@gmail.com , ruifernandes2004@hotmail.com , ruireisesteves@gmail.com , sangel.aesio17@gmail.com , dambroskic@hotmail.com , tiagocardosotavares@icloud.com , tiagommtt@gmail.com , tomasfcrocha@gmail.com , monteirovangogh2003@gmail.com , vanessapisaterrapisaterra@gmail.com , williammacieira223@gmail.com"

alunos = [aluno.strip() for aluno in alunos.split(',')]

alunos = ['Auria',]

from django.contrib.auth.models import User

for email in alunos:
    email = email.strip().lower().replace('\u00a0', '')

    user = User.objects.filter(first_name=email).first()
    if not user:
        print(f"❌ User não existe: '{email}'")
        continue

    aluno = Aluno.objects.filter(user=user).first()
    if not aluno:
        print(f"⚠️ User existe mas não é Aluno: {email}")
        continue

    print(f"✅ Aluno OK: {aluno.nome_completo}")