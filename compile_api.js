import express from "express";
import bodyParser from "body-parser";
import fs from "fs";
import { randomUUID } from 'crypto';
import cors from 'cors';
import { execSync } from "child_process";
import stripAnsi from "strip-ansi";

const app = express();

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.post("/compile", (request, response) => {
    const session_id = randomUUID();
    const payload = request.body;

    const contents = payload.code;
    const flags = payload.flag;

    console.log("Received [POST] on /compile, Session ID =", session_id);

    try {
        fs.mkdirSync(`./cache/${session_id}`);
        for (let i = 0; i < contents.length; i ++) {
            fs.writeFileSync(`./cache/${session_id}/${i}.c0`, contents[i]);
        }
        let paths = [];
        for (let i = 0; i < contents.length; i ++) {
            paths.push(`./cache/${session_id}/${i}.c0`);
        }
        execSync(`cc0 -b ${paths.join(" ")} -o ./cache/${session_id}/out.bc0 ${flags["d"] ? "-d" : ""} > ./cache/${session_id}/out.txt`);

        response.write(JSON.stringify(
            {
                bytecode: fs.readFileSync(`./cache/${session_id}/out.bc0`).toString(),
                c0_output: ""
            }
        ));

        console.log(session_id, "Compile Success");
        // fs.unlinkSync(`./cache/${md5}.bc0`);
    } catch (e){
        console.log(session_id, "Compile Failed");
        console.log(e);
        response.write(JSON.stringify({
            bytecode: "",
            c0_output: stripAnsi(fs.readFileSync(`./cache/${session_id}/out.txt`).toString())
        }));
    } 
    fs.rmSync(`./cache/${session_id}`, {recursive: true, force: true});
    response.end();
    return response;
});

var server = app.listen(8081, () => {
    let host = server.address().address;
    let port = server.address().port;
    console.log(`C0VM.ts server is listening at http://${host}:${port}`);
});
