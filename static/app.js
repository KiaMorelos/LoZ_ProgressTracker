const $addGuide = $(`#add-guide-toggle`)
const $options = $(`#select-journal`)
const $guideForm = $(`#select-j-form`)

const $addTxtGuideBtn = $(`#toggle-add-url`)
const $addTxtGuide = $(`#add-text-guide`)

async function findGamesInPlay(){
    const res = await axios.get('/api/playing')
    const {data} = res
    showForm(data)
}


function showForm(games){
for(let game of games){

    $(`#temp-hidden`).removeClass('hide')
    const optionHTML = `<option value="${game.id}">${game.game_title}</option>`
    $options.append(optionHTML)
}
}

function showTextGuideForm(){
    $addTxtGuide.removeClass('hide')
}


$addGuide.on('click', findGamesInPlay)
$addTxtGuideBtn.on('click', showTextGuideForm)
