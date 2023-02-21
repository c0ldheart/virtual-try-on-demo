import { useState } from "react";
import "./styles.css";
import { PlusOutlined } from '@ant-design/icons';
import { Modal, Upload, Button, Row, Col, Divider, Typography, Form, Select, theme } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
const getBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });


const UploadImage = () => {
  const [fileList2, setFileList2] = useState([]);
  const [imageSrc1, setImageSrc1] = useState(null);
  const [imageSrc2, setImageSrc2] = useState(null);
  const normFile = (e) => {
    setFileList2(e.fileList);
    console.log('Upload event:', e);
    if (Array.isArray(e)) {
      return e;
    }
    return e?.fileList;
  };
  const onFinish = (values) => {
    const imageUrl1 = form.getFieldValue('image1');
    const imageUrl2 = form.getFieldValue('image2');
    console.log('Received values of form: ', values);
    console.log('来自form.getFieldValue(image);: ', imageUrl1);
    // POST到后端
    fetch('http://127.0.0.1:3000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },  // 传递json格式的参数
      body: JSON.stringify({
        image1: imageUrl1,
        image2: imageUrl2,
      }),
    })
      .then(response => response.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        setResponse(url);
      })
  };
  const handleUpload = (options) => {
    const { file, onSuccess } = options;

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://127.0.0.1:3000/upload', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // 上传成功后，将服务器返回的响应结果传递给 onSuccess 回调函数
        console.log('上传成功:', data);
        onSuccess(data, file);
      })
      .catch((error) => {
        console.log('上传失败:', error);
      });
  };


  const { token } = theme.useToken();
  const formStyle = {
    maxWidth: 'none',
    background: token.colorFillAlter,
    borderRadius: token.borderRadiusLG,
    padding: 24,
  };
  const [response, setResponse] = useState("");
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [previewTitle, setPreviewTitle] = useState('');

  const [fileList, setFileList] = useState([
    // {
    //   uid: '-1',
    //   name: 'image.png',
    //   status: 'done',
    //   url: 'https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png',
    // },

  ]);
  const { Title, Paragraph, Text, Link } = Typography;
  const [form] = Form.useForm();
  const handleCancel = () => setPreviewOpen(false);
  const handlePreview = async (file) => {
    if (!file.url && !file.preview) {
      file.preview = await getBase64(file.originFileObj);
    }
    setPreviewImage(file.url || file.preview);
    setPreviewOpen(true);
    setPreviewTitle(file.name || file.url.substring(file.url.lastIndexOf('/') + 1));
  };
  const handleChange1 = info => {

    setImageSrc1(URL.createObjectURL(info.file.originFileObj));
    console.log("info", info);
    let filelist = info.fileList;
    setFileList(filelist);
    console.log('filelist:    ', filelist)
    const curFile = info.file;
    console.log('curFile:    ', curFile)
    console.log('curFile.response:    ', curFile.response)
    if (curFile.response && curFile.response.errno === 0) {
      console.log('上传成功')
    }
    if (curFile.response && curFile.response.errno !== 0) {
      console.log(curFile.response.errmsg)
    }
  }
  const handleChange2 = info => {

    setImageSrc2(URL.createObjectURL(info.file.originFileObj));
  }
  const uploadButton = (
    <div>
      <PlusOutlined />
      <div
        style={{
          marginTop: 8,
        }}
      >
        Upload
      </div>
    </div>
  );

  return (
    <>
      <Form
        form={form}
        name="tryon"
        // {...formItemLayout}
        onFinish={onFinish}

        style={formStyle}
      >
        <Form.Item label="by">
          <span className="ant-form-text">coldheart</span>
        </Form.Item>
        <Row gutter={24} style={{ display: 'flex', justifyContent: 'center' }}>
          <Col span={8}>
            <Form.Item
              name="image1"
              label="Source Human Image"
              valuePropName="fileList"
              getValueFromEvent={normFile}
              extra="选择人物图片（尽量姿势和背景颜色简单）"
            >
              <Upload
                customRequest={handleUpload}
                listType="picture"
                defaultFileList={[...fileList]}
                onPreview={handlePreview}
                onChange={handleChange1}
                maxCount={1}
              >
                <Button icon={<UploadOutlined />}>Upload</Button>
                {/* {fileList.length >= 1 ? null : uploadButton} */}
              </Upload>
            </Form.Item>
          </Col>

          <Col span={8} offset={4}>
            <Form.Item
              name="image2"
              label="Target Cloth Image"
              valuePropName="fileList"
              getValueFromEvent={normFile}
              extra="选择衣物图片（背景白色）"
            >
              <Upload
                listType="picture"
                customRequest={handleUpload}
                defaultFileList={[...fileList2]}
                onPreview={handlePreview}
                onChange={handleChange2}
                maxCount={1}
              >
                <Button icon={<UploadOutlined />}>Upload</Button>
                {/* {fileList.length >= 1 ? null : uploadButton} */}
              </Upload>
            </Form.Item>
          </Col>
        </Row>

        <Row
          span={24}
        >
          <Col span={24}
            style={{
              textAlign: 'center',
            }}>
            <Button type="primary" htmlType="submit">
              Try On
            </Button>

            <Button
              style={{
                margin: '0 8px',
              }}
              onClick={() => {
                // form.resetFields();
                form.setFieldsValue({
                  image1: null,
                  image2: null,
                });
                setResponse(null);
                setImageSrc1([]);
                setImageSrc2([]);
              }}
            >
              Reset
            </Button>
          </Col>
        </Row>
      </Form>
      <Divider>Result</Divider>

      <div style={{
        lineHeight: '200px',
        textAlign: 'center',
        background: token.colorFillAlter,
        borderRadius: token.borderRadiusLG,
        marginTop: 16,
      }}>Tryon Result
        <Row>
          <Col span={8}>
            <div className="result-container">
              <img
                // src={form.getFieldValue("image1")?.[0]?.thumbUrl}
                src={imageSrc1}
                width="300vw"
                alt=""
              />
            </div>
          </Col>
          <Col span={8}>
            {response && (
              <div className="result-container">
                <img src={response} alt="Merged Image" width="300vw" />
              </div>
            )}
          </Col>
          <Col span={8}>
            <div className="result-container">
              <img id="result-image"
                // src={form.getFieldValue("image2")?.[0]?.thumbUrl}
                src={imageSrc2}
                width="300vw"
                alt=""
              />
            </div>
          </Col>

        </Row>
      </div>

      <Modal open={previewOpen} title={previewTitle} footer={null} onCancel={handleCancel}>
        <img
          alt="example"
          style={{
            width: '100%',
          }}
          src={previewImage}
        />
      </Modal>
    </>
  );
};

export default UploadImage;
