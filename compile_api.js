import express from "express";
import bodyParser from "body-parser";
import fs from "fs";
import crypto from "crypto";
import stripAnsi from 'strip-ansi';
import cors from 'cors';
import { execSync } from "child_process";

const app = express();

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.post("/compile", (request, response) => {
    const payload = request.body
    const md5 = crypto.createHash("md5").update(JSON.stringify(request.body)).digest('hex');
    let cc0_output = "";
    fs.writeFileSync(`./cache/${md5}.c0`, payload.code);
    try {
        cc0_output = execSync(`cc0 -b ./cache/${md5}.c0 -o ./cache/${md5}.bc0`);
        response.write(JSON.stringify(
            {
                bytecode: fs.readFileSync(`./cache/${md5}.bc0`).toString()
            }
        ));
        console.log("Compile Success");
    } catch (e){
        console.log("Compile Failed");
        fs.unlinkSync(`./cache/${md5}.c0`);
    }
    response.end();
    console.log("Received [POST] on /compile");
    return response;
});

var server = app.listen(8081, () => {
    let host = server.address().address;
    let port = server.address().port;
    console.log(`C0VM.ts server is listening at http://${host}:${port}`);
});
