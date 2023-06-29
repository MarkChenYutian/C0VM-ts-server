# Deploy Instructions

To re-deploy a C0VM.ts version, do the following steps:

1. Use `npm run build` in `C0VM-ts` repository to compile the React project into static files
2. Copy the content in `build` folder (in `C0VM-ts` repo) into the `static` folder in `C0VM-ts-server` repo.
3. Push the changes on `C0VM-ts-server` to GitHub
4. Run the `./auto_update.sh` on remote machine where the website is deployed
