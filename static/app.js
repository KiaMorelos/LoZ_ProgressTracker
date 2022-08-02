const $addGuide = $(`#add-guide-toggle`)
const $options = $(`#select-journal`)
const $guideForm = $(`#select-j-form`)

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


$addGuide.on('click', findGamesInPlay)
