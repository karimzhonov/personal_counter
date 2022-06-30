const init_admin_url = async () => {
    document.querySelector('#admin_url').addEventListener('click', async () => {
        const config = await eel.config()()
        window.location = config['admin_url']
    })
}

const init_capture_button = async () => {
    let config = await eel.config()()
    for (let capture in config.captures) {
        capture = config.captures[capture]
        const btn = document.querySelector(`.button_${capture.name}`)
        btn.addEventListener('click', () => {
            console.log("click")
            document.querySelector(`div[data-info="${capture.name}"]`)
                .querySelector(".profiles_list").innerHTML = ""
        })
    }
}

const init_config = async () => {
    document.querySelector('.config').innerHTML = await eel.show_config()()
    document.querySelector('#config_submit').addEventListener('click', async () => {
        const config = document.querySelector('#config').value
        let bool = await eel.update_config(config)()
        if (bool) {
            document.querySelector('.config').innerHTML = ''
            await init_captures()
            document.querySelector('#btn').innerHTML = ''
        } else {
            document.querySelector('#config_help').style.color = 'red'
        }
    })
}

const init_captures = async () => {
    document.querySelector('.captures').innerHTML = await eel.show_captures()()
    await init_capture_button()
    await update()
}

const update = async () => {
    const config = await eel.config()()
    for (let capture in config.captures) {
        capture = config.captures[capture]
        await update_capture(capture)
    }
}

const update_capture = async (capture) => {
    setInterval(update_frame, 1, capture)
    setInterval(update_data, capture.timeout, capture)
}

const update_frame = async (capture) => {
    const image = await eel.get_frame(capture.name)()
    document.querySelector(`div[data-capture="${capture.name}"]`).innerHTML =
        `<img src="data:image/jpeg;base64, ${image[0]}" class="img-fluid rounded-start" alt="frame">`
}

const update_data = async (capture) => {
    const profiles = await eel.get_profiles(capture.name)()
    let html = ''
    const profiles_card = document.querySelectorAll(".profile_card")
    for (let profile in profiles) {
        profile = profiles[profile]
        let status_add = true
        for (let i = 0; i < profiles_card.length; i++) {
            let profile_card = profiles_card[i]
            if (parseInt(profile_card.getAttribute("data-profile-id")) === parseInt(profile.id)) {
                status_add = false
                break
            }
        }
        if (status_add) {
            html += `
                <div class="card mb-3 p-2">
                    <div class="row g-0">
                        <div class="col-md-4 p-2" data-capture="{{ name }}">
                            <img src="data:image/jpeg;base64, ${profile.image}" style="width: 100%" class="img-fluid rounded-start" alt="frame">
                        </div>
                        <div class="col-md-8">
                            <div class="card-body profile_card" data-profile-id="${profile.id}">
                                <div class="card-text"><strong>Profile Id: </strong>${profile.id}</div>
                                <div class="card-text"><strong>Full name: </strong>${profile.fullname}</div>
                                <div class="card-text"><strong>Visits count: </strong>${profile.visit_count}</div>
                                <div class="card-text"><strong>Last visit: </strong>${profile.last_visit.replace('T', ' ')}</div>
                            </div>
                        </div>
                    </div>
                </div>`
        }
    }
    document.querySelector(`div[data-info="${capture.name}"]`)
        .querySelector(".profiles_list").insertAdjacentHTML('beforeend', html)
}

window.onload = async () => {
    await init_config();
    await init_admin_url()
}
window.onbeforeunload = async () => await eel.close()()