# TechGuide AI

O TechGuide AI é um projeto de código aberto que se baseia no [TechGuide.sh](https://github.com/alura/techguide/)
desenvolvido pela [Alura](https://www.alura.com.br/). A partir da descrição de uma vaga de emprego o 
TechGuide AI irá utilizar os recursos de embedding e de IA generativa do Gemini
para descrever melhor a vaga, determinar as especialidades necessárias e sugerir 
objetivos do candidato e apresentar os cursos da Alura mais adequados para ajudar
o candidato a atingir esses objetivos.

Espera-se que por meio dessa ferramenta o candidato possa ter uma visão mais clara
de qual trajeto ele deve seguir para estar preparado para aplicar para uma vaga de
tecnologia.


## Preparação do ambiente

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Atualização da ferramenta com nova versão do TechGuide (opcional)

O repositório já contempla a versão do TechGuide.sh que foi utilizada para treinar.

Isso pode ser encontrado nos arquivos [cards.json](data/cards.json) e 
[guides.json](data/guides.json),

Vale dizer que o embedding por meio do Gemini é feito com base nesses arquivos e 
também armazenados nos arquivos [cards_embedding.json](data/cards_embedding.json) e
[guides_embedding.json](data/guides_embedding.json).

Obviamente o TechGuide irá evoluir e será necessário refazer esse procedimento
de download e de embedding. Para isso basta executar:

```shell
python -m techguideai.collector
```

## Execução

Para executar o TechGuide AI basta executar:

```shell
python -m techguideai.planner --job_description "Descrição da vaga"
```

É possível também definir o quão profundo pretende-se explorar o 
TechGuide. O conceito de profundidade é definido como a quantidade
de layers de especialidades que o TechGuide irá explorar. Por padrão o valor é de 4.
Para definir a profundidade basta passar o argumento `--depth` seguido do valor desejado.

```shell
python -m techguideai.planner --job_description "Descrição da vaga" --depth 3
```

É possível também definir o quanto tempo você tem disponível para se preparar
para a vaga. O conceito de tempo é definido como a quantidade de cards do TechGuide
que serão considerados. Por padrão o valor é de 8. Para a disponibilidade, 
basta passar o argumento `--availability` seguido do valor desejado.

```shell
python -m techguideai.planner --job_description "Descrição da vaga" --availability 4
```

