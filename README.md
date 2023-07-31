
# AWS CodeWhisperer Demo

CodeWhisperer makes it more efficient for developers to use AWS services by providing code suggestions that are optimized for AWS APIs including Amazon Elastic Compute Cloud (Amazon EC2), AWS Lambda, and Amazon Simple Storage Service (Amazon S3). As you write code in your IDE, CodeWhisperer automatically analyzes your code and comments. It makes a suggestion using the relevant cloud services and public software libraries for the desired functionality, and then it recommends code snippets that meet AWS best practices.

## Setup information

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```
After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```
<br/>

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```
<br/>

Setup AWS CLI Credentials.
  1) Export via environment variables.
  ``` 
  export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
  export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  export AWS_DEFAULT_REGION=us-west-2
  ```
  2) Configure AWS profile.
    Please check the [documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

<br/>

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```
To deploy the solution please run the following command.

```
$ cdk deploy
```
<br/>
After deployment succeed, you should see the following output

```
API_GW_ENDPOINT=***
```
You can access the app using this endpoint.

Enjoy!

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

