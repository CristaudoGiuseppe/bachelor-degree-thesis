const Discord = require('discord.js');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

const bot = new Discord.Client();

const token = 'NzEzNTA2MDY0NjQ5MTU4NzQx.XshGTg.RAH34PAgPgDVoV6bm8uQwtutTIE';
const prefix = '!'

function sendEmbed (title, description, color, message) {
    const embed = {
        "title": title,
        "description": description,
        //"url": "https://discordapp.com",
        "color": color,
        "timestamp": new Date(),
        "footer": {
          //"icon_url": bot.user.avatarURL(),
          "text": "CrissAIO Auth"
        },
        /*"thumbnail": {
          "url": "https://cdn.discordapp.com/embed/avatars/0.png"
        },
        "image": {
          "url": "https://cdn.discordapp.com/embed/avatars/0.png"
        },*/
        "author": {
          "name": "CrissAIO",
          "icon_url": 'https://i.imgur.com/a3UXhvS.png'
        }
    };
    message.channel.send("", { embed });
}

function setRole(message, id) {
    const guild = bot.guilds.cache.get('716588647780188182'); /* GUILD ID del Canale*/
    // this looks for the users id in the guild
    var isMember = guild.members.cache.get(id)

    // if true
    if (isMember) {
        // then add the role
        isMember.roles.add('718850876680437760') /* ID del ruolo */
        .catch(console.error);
    } else {
        // if not true. send the user this message
        sendEmbed('Error setting role', 'Probably you are not in CrissAIO Server', 15158332, message)
        //message.reply('You are not part of CrissAIO Server')
    }
}

function createKey() {

    var key = "CRISS-";
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    var temp = 0;

    while (key.length < 25) {
        while(temp != 4){
            key += characters.charAt(Math.floor(Math.random() * characters.length))
            temp++
        }

        key += '-';
        temp = 0;
    }

    key = key.substring(0, key.length - 1);

    return key;
}

bot.on('ready', () => {
    bot.user.setStatus('online');
    bot.user.setActivity("CrissAIO"); 
});

bot.on('guildMemberAdd', (message) => {    
    /*

    BACKUP VERSIONE VECCHIA

    user_id = message.user.username+'#'+message.user.discriminator
    fs.createReadStream('beta_tester.csv')
    .pipe(csv())
    .on('data', (row) => {
        if(row.USER == user_id){
            const embed = {
                "title": "Welcome on CrissAIO's server",
                "description": "This is your key: ||"+row.KEY+"||\nPlease bind it using command !bind.\nHave fun 😀",
                "color": 0xff00dd,
                "timestamp": new Date(),
                "footer": {
                    "icon_url": "https://i.imgur.com/a3UXhvS.png",
                    "text": "CrissAIO Authentication"
                }
            };
            message.send("", { embed });
        }
    })
    */
	
	var key = createKey();
	var content = '\n"'+key+'","OK","","","",""';
   
	const fd = fs.openSync('key.csv', 'a');
	fs.writeSync(fd, content);

	const embed = {
		"title": "Welcome on CrissAIO's server",
		"description": "This is your key: ||"+key+"||\nPlease bind it using command !bind.\nHave fun 😀",
		"color": 0xff00dd,
		"timestamp": new Date(),
		"footer": {
			"icon_url": "https://i.imgur.com/a3UXhvS.png",
			"text": "CrissAIO Authentication"
		}
	};

	message.send("", { embed });
})

bot.on('message', (message) => {

    /* Se il messaggio e' stato inviato nei DM allora procedi, altrimenti no */
    if(message.guild === null) { 

        let args = message.content.substring(prefix.length).split(" ");
        var key = args[1];
        var user = message.author.tag.replace('#',':');
        var id = message.author.id;

        /* SE DOVESSE SERVIRE
        var role = message.guild.roles.cache.find(r => r.name === 'Beta Tester'); //Get Roles
        message.member.roles.add(role);
        */

        switch(args[0]){
            
            case 'bind':
                http.get('http://95.179.183.203:5000/bind?key'+key+"?name"+user+"?id"+id, resp => {

                    console.log("StatusCode: "+ resp.statusCode);
                    
                    switch(resp.statusCode){
                        case 200:
                            sendEmbed("License actived", "You have activated your key "+key, 3066993, message);
                            setRole(message, id)
                            break;
                        case 503:
                            sendEmbed("License not actived", "Your "+key+" is already binded to another Discord", 15158332, message);
                            break;
                        case 404:
                            sendEmbed("License not actived", "Your key "+key+" does not exist", 15158332, message);
                            break;
                        case 405:
                            sendEmbed("License not actived", "Your key "+key+" is already binded to this Discord", 15158332, message);
                            break;
                    }

                }).on("error", (err) => {
                    sendEmbed("License not actived", "Probably CrissAIO's server is offline, contact us on Discord", 15158332, message);
                    console.log("Error: " + err.message);
                });
                break;

            case 'reset':
                http.get('http://95.179.183.203:5000/reset?key'+args[1]+"?name"+user+"?id"+id, resp => {

                    console.log("StatusCode: "+ resp.statusCode);

                    switch(resp.statusCode){
                        case 200:
                            sendEmbed("Key reset", "Your key "+key+" has been resetted", 3066993, message);
                            break;
                        case 503:
                            sendEmbed("Key not reset", "Your key "+key+" not binded to this Discord account", 15158332, message);
                            break;
                        case 404:
                            sendEmbed("Key not reset", "Your key "+key+" does not exist", 15158332, message);
                            break;
                        case 405:
                            sendEmbed("Key not reset", "Your key "+key+" is already reset", 15158332, message);
                            break;
                    }

                    }).on("error", (err) => {
                        sendEmbed("Key not reset", "Probably CrissAIO's server is offline, contact us on Discord", 15158332, message);
                        console.log("Error: " + err.message);
                    });
                break;
        }
    }
});

bot.login(token);