const init_admin_url = async () => {
    document.querySelector('#admin_url').value = await eel.admin_url()()
    document.querySelector('#btn_admin_url').addEventListener('click', async () => {
        window.location = document.querySelector('#admin_url').value
    })
}

const init_add_capture = async () => {
    await update()
    document.querySelector('.captures').innerHTML = `
    ${await eel.show_captures()()}
    ${await eel.show_add_capture()()}`
    document.querySelector('#btn_add_capture').addEventListener('click', async () => {
        const rotate_angle = {
            "0": null,
            "90": 0,
            "180": 1,
            "270": 2,
        }
        let capture_name = document.querySelector('#capture_name')
        let capture_ip = document.querySelector('#capture_ip')
        let server_ip = document.querySelector('#server_ip')
        let capture_rotate = document.querySelector('#capture_rotate')
        let capture_timeout = document.querySelector('#capture_timeout')
        let capture = {
            name: capture_name.value,
            capture: capture_ip.value,
            server: server_ip.value,
            rotate: rotate_angle[capture_rotate.value],
            timeout: capture_timeout.value
        }
        const capture_html = await eel.add_capture(JSON.stringify(capture))()
        await update()
        document.querySelector('#add_capture').insertAdjacentHTML('beforebegin', capture_html)
        await init_capture_button()
        capture_name.value = null
        capture_ip.value = null
        server_ip.value = null
        capture_rotate.value = 0
        capture_timeout.value = null
    })
}

const init_capture_button = async () => {
    let captures = await eel.captures()()
    for (let capture in captures) {
        capture = captures[capture]
        const btn = document.querySelector(`.button_${capture.name}`)
        btn.addEventListener('click', () => {
            document.querySelector(`div[data-info="${capture.name}"]`)
                .querySelector(".profiles_list").innerHTML = ""
        })
    }
}

const update = async () => {
    try {
        const captures = await eel.captures()()
        const capture_cards = document.querySelectorAll('.capture')
        for (let capture in captures) {
            capture = captures[capture]
            let include = false
            for (let i = 0; i < capture_cards.length; i++) {
                if (capture_cards[i].getAttribute('data-capture') === capture.name) {
                    include = true
                    break
                }
            }
            if (!include) {
                await update_capture(capture)
            }
        }
    } catch (e) {
    }
}

const update_capture = async (capture) => {
    console.log("Start update capture: ", capture.name)
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
                <div class="card mb-1 p-2">
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
    await init_admin_url()
    await init_add_capture()
}
window.onbeforeunload = async () => await eel.close()()