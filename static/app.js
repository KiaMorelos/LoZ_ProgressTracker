const $addGuide = $(`.add-guide-toggle`)
const $options = $(`.guide-select`)
const $guideForm = $(`.select-j-form`)
const $guideContainer = $(`#misc-guides`)

const $addTxtGuideBtn = $(`#toggle-add-url-on`)
const $hideBtn = $(`#hide-btn`)
const $addTxtGuide = $(`#add-text-guide`)

async function findGamesInPlay(){
    const res = await axios.get('/api/playing')
    const {data} = res
    showForm(data)
}


function showForm(games){
for(let game of games){

    $(`.temp-hidden`).removeClass('hide')
    const optionHTML = `<option value="${game.id}">${game.game_title}</option>`
    $options.append(optionHTML)
}
}

function showTextGuideForm(){
    $addTxtGuide.removeClass('hide')
}

function hideTextGuideForm(){
    $addTxtGuide.addClass('hide')
}


$guideContainer.on('click', 'button', findGamesInPlay)
$addTxtGuideBtn.on('click', showTextGuideForm)
$hideBtn.on('click', hideTextGuideForm)
