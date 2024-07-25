MC="/usr/bin/mc"
bucket_exist() {
  CMD=$(${MC} ls memesis/$MINIO_BUCKET > /dev/null 2>&1)
  return $?
}
/usr/bin/mc config host add  --api S3v4 memesis http://minio-1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD;
if ! bucket_exist ; then
    ${MC} mb memesis/$MINIO_BUCKET
fi
${MC} admin user add memesis $MINIO_USER $MINIO_PASSWORD
${MC} admin group add memesis $MINIO_USER_GROUP $MINIO_USER
${MC} admin policy detach memesis/$MINIO_BUCKET readwrite --group users
${MC} admin policy detach memesis/$MINIO_BUCKET readwrite --group users

${MC} admin policy attach memesis/$MINIO_BUCKET readwrite --group users
