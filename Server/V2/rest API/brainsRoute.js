const { ok } = require('assert');
const { count } = require('console');
const { response } = require('express');
const express = require('express');
const { Module } = require('module');
const route = express.Router();

const { MongoClient } = require('mongodb');

const DBclient = new MongoClient ("mongodb://localhost:27017/");

//-----------------------------------------------------------------------------------------------------------------
let controleBuffer = [];

//-----------------------------------------------------------------------------------------------------------------

 async function test(client)
{
    try {
        
        await client.connect();
         
        await client.db("admin").command({ ping: 1 });
        console.log("Connection tested successfully to DBserver");
      } finally {
         
        await client.close();
      }
}
async function getData(search)
{
    try{    DBclient.connect();
        let testDB = await DBclient.db("testDB");
        let testCollection = await testDB.collection("testCollection");
    let cursor = await testCollection.find(search)
    let data = await cursor.toArray();
    return data;
    }finally{
    await DBclient.close();
    }
}

async function getDataFirst(search)
{
    try{    DBclient.connect();
        let testDB = await DBclient.db("testDB");
        let testCollection = await testDB.collection("testCollection");
    return await testCollection.findOne(search)
    }finally{
    await DBclient.close();
    }
}

async function getData5(search)
{
    try{    DBclient.connect();
        let testDB = await DBclient.db("testDB");
        let testCollection = await testDB.collection("testCollection");
    let cursor = await testCollection.find(search).limit(5)
    let data = await cursor.toArray();
    return data;
    }finally{
    await DBclient.close();
    }
}
async function sendData(data)
 {
try{
    DBclient.connect();
    let testDB = await DBclient.db("testDB");
    let testCollection = await testDB.collection("testCollection");
    let returndata = await testCollection.insertOne(data)
    //console.log(returndata)
    return returndata
}finally{
    await DBclient.close();
}
}
function ringbufferAdd(buffer = [],ellement)
{
    if(buffer.length==10){
        buffer.push(ellement)
        buffer.shift()
    }else{
        buffer.push(ellement)
    }
    return buffer;
}

async function getDataAndFilter(searce, filterDict)
{
    try{    DBclient.connect();
        let testDB = await DBclient.db("testDB");
        let testCollection = await testDB.collection("testCollection");
    let cursor = await testCollection.find(searce).project(filterDict).limit(100)
    let data = await cursor.toArray();
    return data;
    }finally{
    await DBclient.close();
    }
}

async function getDistinctHelmetData()
{
    try{    DBclient.connect();
        let testDB = await DBclient.db("testDB");
        let testCollection = await testDB.collection("testCollection");
    return await testCollection.distinct("HelmName")
    }finally{
    await DBclient.close();
    }
}

//-----------------------------------------------------------------------------------------------------------------

test(DBclient).catch(console.log)
   

   route.get('/getByNameForTime/:timestamp/:name',async (req,res) =>{

        // console.log(req.params);
        let search = {HelmName: req.params.name, TimeStamp: new Date(req.params.timestamp)}
        // console.log(search)
        let returndata = await getData(search);
        res.json(returndata);
        });

    // route.get('/getByName/:name',async (req,res) =>{
    route.get('/getTimestampsByName/:name',async (req,res) =>{


        // let returndata = await getDataAndFilter({HelmName: req.params.name}, { 'fields': {HelmName: 1, TimeStamp: 1, Channels: 0}})
        let returndata = await getDataAndFilter({HelmName: req.params.name}, {"TimeStamp": 1})


        console.log(returndata)
        res.json(returndata);
        });
    
    route.get('/getFirstPackageByName/:name',async (req,res) =>{


        // let returndata = await getDataAndFilter({HelmName: req.params.name}, { 'fields': {HelmName: 1, TimeStamp: 1, Channels: 0}})
        let returndata = await getDataFirst({HelmName: req.params.name})


        console.log(returndata)
        res.json(returndata);
        });
        
    route.get('/getNext5PackagesByName/:name/:lastTimestamp',async (req,res) =>{


        // let returndata = await getDataAndFilter({HelmName: req.params.name}, { 'fields': {HelmName: 1, TimeStamp: 1, Channels: 0}})
        let returndata = await getData5({HelmName: req.params.name, TimeStamp: {$gt: new Date(req.params.lastTimestamp)}}, {"TimeStamp": 1})


        console.log(returndata)
        res.json(returndata);
        });


    route.get('/getAllHelmets',async (req,res) =>{


        // let returndata = await getDataAndFilter({HelmName: req.params.name}, { 'fields': {HelmName: 1, TimeStamp: 1, Channels: 0}})
        let returndata = await getDistinctHelmetData()


        console.log(returndata)
        res.json(returndata);
        });
        

    route.get('/getByName/:name',async (req,res) =>{

        let returndata = await getData({HelmName: req.params.name});
        res.json(returndata);
        });

    route.get('/getAllData',async (req,res) =>{

        let returndata = await getData({});
        res.json(returndata);
    });


    counter = 0
    route.post('/postData', express.json(),async (req,res)=>{
        try {
            if (counter < 10)
            {
                console.log("faking error") 
                throw 'fakeeee'               
            }
            let data = req.body;
            // console.log(data);
            data.TimeStamp = new Date(data.TimeStamp);
            console.log(data.TimeStamp);
            await sendData(data);
            Success = true;
            console.log('package received')

        } catch (error)
        {     
            counter++;
            Success = false;
            console.log(counter)
            console.log('package received, but error occurred, requesting retry')
        }
        finally
        {
            res.send(Success)
        }
        
    });

    module.exports = route;