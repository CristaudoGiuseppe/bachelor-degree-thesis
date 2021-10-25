const Discord = require('discord.js');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

const bot = new Discord.Client();

const token = 'NzcwOTQ1MTI0Njg3MTUxMTI0.X5k8mQ.oOw2no0RvWcac8qzXv4LGutYW-4';
const prefix = '!'

bot.on('ready', () => {
    bot.user.setStatus('online');
    bot.user.setActivity("CrissAIO"); 
});

bot.on('message', async message => {

    /* Se il messaggio e' stato inviato nei DM allora procedi, altrimenti no */
    if(message.guild === null) return;

    let args = message.content.substring(prefix.length).split(" ");

    if(args[0] === 'reaction'){
        let embed = new Discord.MessageEmbed()
        .setTitle('Reaction Roles')
        .setDescription('Simply click one or more of the following icons in order to get the desired role(s).\nClick again to remove the role.')
        .setThumbnail('https://i.imgur.com/a3UXhvS.png')
        .addFields(
            { name: 'IT 🇮🇹', value: 'Choose this one for IT restocks' },
            { name: 'EU 🇪🇺', value: 'Choose this one for EU restocks' }
        )
        .setColor(0xff00dd)
        .setFooter('CrissAIO', 'https://i.imgur.com/a3UXhvS.png');

        let msgEmbed = await message.channel.send(embed)
        msgEmbed.react('🇮🇹')
        msgEmbed.react('🇪🇺')
    }

});

bot.on("messageReactionAdd", async (reaction, user) => {
    if (reaction.message.partial) await reaction.message.fetch();
    if (reaction.partial) await reaction.fetch();

    if(user.bot) return;
    if(!reaction.message.guild) return;

    if (reaction.message.channel.id === "779681409546715166") {
        if(reaction.emoji.name === '🇮🇹'){
            await reaction.message.guild.members.cache.get(user.id).roles.add("779666404328603669")
        }

        if(reaction.emoji.name === '🇪🇺'){
            await reaction.message.guild.members.cache.get(user.id).roles.add("779666449370841109")
        }

    }
});

bot.on("messageReactionRemove", async (reaction, user) => {
    if (reaction.message.partial) await reaction.message.fetch();
    if (reaction.partial) await reaction.fetch();

    if(user.bot) return;
    if(!reaction.message.guild) return;

    if (reaction.message.channel.id === "779681409546715166") {
        if(reaction.emoji.name === '🇮🇹'){
            await reaction.message.guild.members.cache.get(user.id).roles.remove("779666404328603669")
        }

        if(reaction.emoji.name === '🇪🇺'){
            await reaction.message.guild.members.cache.get(user.id).roles.remove("779666449370841109")
        }

    }
})

bot.login(token);