
const amqp = require('amqplib/callback_api');
const { MongoClient } = require('mongodb');
const DBclient = new MongoClient ("mongodb://localhost:27017/");
const monDb = "testDB";
const monColection = "TestCol2"
DBclient.connect();

//MongoDB_functions_______________________________________________
async function sendData(data){
    try{
    let testDB = await DBclient.db(monDb);
    let testCollection = await testDB.collection(monColection);

let returndata = await testCollection.insertOne(data)
    return returndata
    }
    catch(err){
    console.log("error mongoDB");
    console.log(err.name);
    }
}
//_______________________________________________________________

    

// making connection with RabbitMQ
amqp.connect('amqp://localhost', function(error0, connection) {
    if (error0) {
        throw error0;
    }
    connection.createChannel(function(error1, channel) {
        if (error1) { throw error1; }

        var queue = 'brains'; // work queue for OpenBCI data
        channel.prefetch(1)
        channel.assertQueue(queue,{ durable: true });
        console.log(" [X] recieving Data from queue: %s. To exit press CTRL+C", queue);
        channel.consume(queue, (msg) => {
            var data = JSON.parse(msg.content.toString())

        console.log(" [x] Received %s",data.HelmName);
        
        sendData(data);

    },{ noAck: true });

    });
});
