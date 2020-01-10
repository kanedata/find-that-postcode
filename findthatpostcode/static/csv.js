function clean_postcode(pc) {
    if (typeof pc === 'string' || pc instanceof String) {
        pc = pc.toUpperCase().replace(/[^A-Z0-9]/, '');
        return pc.slice(0, -3) + " " + pc.slice(-3);
    }
    return pc;
}

function hash_postcode(pc) {
    pc = pc.toLowerCase().replace(/[^a-z0-9]/, '');
    var pchash = CryptoJS.MD5(pc);
    return pchash.toString(CryptoJS.enc.Hex).slice(0, 3);
}

function update_fields_table(results, table) {
    table.innerHTML = '';
    var header_row = document.createElement('tr');
    for (const f of ['', 'Field name', 'Example values']) {
        header_row.appendChild(document.createElement('th')).appendChild(document.createTextNode(f));
    }
    header_row.childNodes[1].classList.add('w5');
    table.appendChild(header_row);
    for (const f of results.meta.fields) {
        var row = document.createElement('tr');
        var radio = row.appendChild(document.createElement('th')).appendChild(document.createElement('input'))
        radio.setAttribute('type', 'radio');
        radio.setAttribute('name', 'postcode_field');
        radio.setAttribute('value', f);
        if (f.toLowerCase().replace(/[^a-z]/gi, '') == "postcode") {
            radio.setAttribute('checked', true);
            document.getElementById('column_name').setAttribute('value', f);
        }
        radio.onclick = function () {
            if (this.checked) {
                document.getElementById('column_name').setAttribute('value', this.value);
            }
        }
        row.appendChild(document.createElement('th')).appendChild(document.createTextNode(f));
        var field = document.createElement('td');
        var field_ul = document.createElement('ul');
        field_ul.classList.add('list', 'pa0', 'ma0');
        let values_seen = []
        for (const r of results.data) {
            if ((!values_seen.includes(r[f])) && (r[f] != '') && (typeof r[f] != 'undefined')) {
                var field_li = field_ul.appendChild(document.createElement('li'))
                field_li.classList.add('dib', 'code', 'mr2', 'bg-light-gray', 'mb1', 'tl', 'truncate', 'mw5');
                field_li.appendChild(document.createTextNode(r[f]));
                values_seen.push(r[f]);
            }
            if(values_seen.length >= 5){
                break;
            }
        }
        field.appendChild(field_ul)
        row.appendChild(field);
        table.appendChild(row);
    }
}

function get_results(hashes, fields_to_add) {
    const url_parameters = new URLSearchParams(fields_to_add.map(f => ['properties', f]));
    var urls = Array.from(hashes.values()).map(hash => {
        var url = new URL(hash_url.replace('xxx', hash));
        url.search = url_parameters.toString();
        return url;
    });
    return Promise.all(urls.map(url => 
        fetch(url)
            .then(res => res.json())
            .then((data) => {
                return Object.fromEntries(data.data.map(i => [i["id"], i]));
            })
            .catch((error) => {
                console.log('Error: ', error)
            })
    ))
    .then(data => Object.assign({}, ...data))
}

function parse_fields_to_add(fields){

    if(fields.includes("latlng")){
        fields.splice(fields.indexOf("latlng"), 1, "lat", "long");
    }

    if(fields.includes("estnrth")){
        fields.splice(fields.indexOf("estnrth"), 1, "oseast1m", "osnrth1m");
    }

    if(fields.includes("lep")){
        fields.splice(fields.indexOf("lep"), 1, "lep1", "lep2");
    }

    if(fields.includes("lep_name")){
        fields.splice(fields.indexOf("lep_name"), 1, "lep1_name", "lep2_name");
    }
    return fields;
}

function openSaveFileDialog(data, filename, mimetype) {
// from: https://github.com/mholt/PapaParse/issues/175#issuecomment-395978144

    if (!data) return;

    var blob = data.constructor !== Blob
        ? new Blob([data], { type: mimetype || 'application/octet-stream' })
        : data;

    if (navigator.msSaveBlob) {
        navigator.msSaveBlob(blob, filename);
        return;
    }

    var lnk = document.createElement('a'),
        url = window.URL,
        objectURL;

    if (mimetype) {
        lnk.type = mimetype;
    }

    lnk.download = filename || 'untitled';
    lnk.href = objectURL = url.createObjectURL(blob);
    lnk.dispatchEvent(new MouseEvent('click'));
    setTimeout(url.revokeObjectURL.bind(url, objectURL));

}

function create_new_file(results, new_data, column_name, fields_to_add){
    return Papa.unparse({
        fields: results.meta.fields.concat(fields_to_add),
        data: results.data.map(row => Object.assign(
            row, 
            new_data[clean_postcode(row[column_name])]
        ))
    });
}

function click_download(results, filename) {
    var column_name = document.getElementById('column_name').value;

    var hashes = new Set(Array.from(results.data).filter(r => r[column_name]).map(r => hash_postcode(r[column_name])));
    var fields_to_add = parse_fields_to_add(
        Array.from(document.getElementsByName("fields"))
             .filter(i => i.checked)
             .map(i => i.value)
    );

    get_results(hashes, fields_to_add).then(data => openSaveFileDialog(
        create_new_file(
            results,
            data,
            column_name,
            fields_to_add,
        ),
        filename.replace(".csv", "-geo.csv")
    ));
}

var file = document.getElementById("csvfile");
file.onchange = function () {
    if (file.files.length > 0) {
        document.getElementById('csvfilename').innerHTML = file.files[0].name;
        document.getElementById('csvpreview').classList.remove("dn");
        document.getElementById('csvpreview').getElementsByTagName('table')[0].innerHTML = '';
        Papa.parse(file.files[0], {
            header: true,
            worker: true,
            complete: function (results) {
                var preview = document.getElementById('csvpreview');
                update_fields_table(results, preview.getElementsByTagName('table')[0]);
                document.getElementById("fetch_postcodes").onclick = function(ev){
                    ev.preventDefault();
                    click_download(results, file.files[0].name);
                } 
            }
        });
    } else {
        document.getElementById('csvfilename').innerHTML = "";
        document.getElementById('csvpreview').classList.add("dn");
    }
};

document.getElementById("select_all_codes").onchange = function (ev) {
    Array.prototype.forEach.call(document.getElementsByName("fields"), function (item) {
        if (!item.value.endsWith("_name")) {
            item.checked = ev.target.checked;
        }
    });
}

document.getElementById("select_all_names").onchange = function (ev) {
    Array.prototype.forEach.call(document.getElementsByName("fields"), function (item) {
        if (item.value.endsWith("_name")) {
            item.checked = ev.target.checked;
        }
    });
}
