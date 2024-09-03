import boto3
import logging
from botocore.exceptions import ClientError
import os

logging.getLogger().setLevel(logging.INFO)
cloudformation_client = boto3.client('cloudformation')

def create_stack(stack_name,template_body, **kwargs): #criando o stack no cloudformation
    cloudformation_client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_IAM','CAPABILITY_NAMED_IAM'],
        TimeoutInMinutes=30,
        OnFailure='ROLLBACK'
    )

    cloudformation_client.get_waiter('stack_create_complete').wait(
        StackName=stack_name,
        WaiterConfig={'delay':5,'MaxAttempts':600}
    )
    cloudformation_client.get_waiter('stack_exists').wait(Stackname=stack_name)
    logging.info(f'CREATE COMPLETE')

def update_stack(stack_name, template_body, **kwargs): #fazendo o update do stack, em caso de erro sinalizar
    try:
        cloudformation_client.update_stack(
            StackName=stack_name,
            Capabilities=['CAPALIBITIES_IAM','CAPABILITIES_NAMED_IAM'],
            TemplateBody=template_body
        )
    
    except ClientError as e:
        if 'No updates are to be performed' in str(e):
            logging.info(f'SKIPPING UPDATE: No updates to be performed at stack {stack_name}')
            return e
    
    cloudformation_client.get_waiter('stack_update_complete').wait(
        StackName=stack_name,
        WaiterConfig={'delay':5,'MaxAttempts':600}
    )

    cloudformation_client.get_waiter('stack_exists').wait(StackName=stack_name)
    logging.info(f'UPDATE COMPLETE')

def get_existing_stacks():
    response = cloudformation_client.list_stacks(
        StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
    )

    return [stack['StackName'] for stack in response['StackSummaries']]


def _get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def create_or_update_stack():
    stack_name = 's3-bucket-ci'
    with open(_get_abs_path('bucket_githubactions.yml')) as f:
        template_body = f.read()

    existing_stack = get_existing_stacks()

    if stack_name in existing_stack:
        logging.info(f'UPDATE STACK {stack_name}')
        update_stack(stack_name,template_body)
    else:
        logging.info(f'CREATING STACK {stack_name}')
        create_stack(stack_name,template_body)

if __name__ == '__main__':
    create_or_update_stack()