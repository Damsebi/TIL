# Today I Learned

공부하면서 헷갈렸거나, 나중에 다시 찾아볼 내용을 정리합니다.

## Git

- [Git 기본 명령어](Git/1-Git-기본-명령어.md)
- [커밋 메시지 작성 가이드](Git/2-커밋-메세지-작성-가이드.md)


## 기초 수학

- [벡터에서 코사인 유사도까지](Math/1-벡터에서-코사인-유사도까지.md)
- [행렬 연산과 딥러닝 레이어](Math/2-행렬연산과-딥러닝레이어.md)
- [특수 행렬과 행렬 연산 성질](Math/3-특수-행렬과-행렬-연산-성질.md)
- [선형 변환의 기하학적 해석](Math/4-선형변환의-기하학적-해석.md)
- [벡터공간과 선형독립](Math/5-벡터공간과-선형독립.md)
- [연립선형방정식과 행렬해법](Math/6-연립선형방정식과-행렬해법.md)
- [고유값·고유벡터의 정의와 기하학적 의미](Math/7-고유값-고유벡터의-정의와-기하학적-의미.md)
- [행렬 대각화와 PCA 구현](Math/8-행렬-대각화와-pca-구현.md)
- [직교성과 최소제곱법](Math/9-직교성과-최소제곱법.md)
- [특이값 분해(SVD)의 구조와 원리](Math/10-svd의-구조와-원리.md)
- [SVD와 PCA의 연결 및 저랭크 응용](Math/11-svd와-pca의-연결-및-저랭크-응용.md)
- [선형대수 종합 미니 프로젝트](Math/12-선형대수-종합-미니-프로젝트.md)
- [벡터·행렬·텐서와 딥러닝 Shape 표기](Math/13-벡터-행렬-텐서와-딥러닝-shape-표기.md)
- [Reshape·Transpose·Broadcasting과 행렬곱 Shape 추론](Math/14-reshape-transpose-broadcasting과-행렬곱-shape-추론.md)
- [Attention Score: 내적과 QKᵀ Shape 추론](Math/15-attention-score-내적과-qk-transpose-shape-추론.md)
- [Softmax·로그확률·Cross Entropy](Math/16-softmax-로그확률과-cross-entropy.md)
- [미분·편미분·Gradient와 Gradient Descent](Math/17-미분-편미분-gradient와-gradient-descent.md)
- [Chain Rule과 Backpropagation](Math/18-chain-rule과-backpropagation.md)


## NumPy

- [Dim, Axis와 Argmax Shape](NumPy/1-dim-axis와-argmax-shape.md)


## 머신러닝

- [하이퍼파라미터 탐색과 교차검증](MachineLearning/5-하이퍼파라미터-탐색과-교차검증.md)


## 딥러닝 기초

### Part 1. 딥러닝 입문과 전체 흐름

- [머신러닝과 딥러닝의 차이](DeepLearningBasic/1-1-머신러닝과-딥러닝의-차이.md)
- [데이터·모델·손실·최적화·평가 흐름](DeepLearningBasic/1-2-데이터-모델-손실-최적화-평가-흐름.md)
- [딥러닝 문제 유형과 입출력 구조 설계](DeepLearningBasic/1-3-딥러닝-문제-유형과-입출력-구조-설계.md)
- [기본 코드 구조 읽기](DeepLearningBasic/1-4-기본-코드-구조-읽기.md)

### Part 2. Tensor와 실행 환경

- [Tensor 생성과 dtype·shape 확인](DeepLearningBasic/2-1-tensor-생성과-dtype-shape-확인.md)
- [Batch Dimension과 Broadcasting](DeepLearningBasic/2-2-batch-dimension과-broadcasting.md)
- [CPU·GPU Device와 `.to(device)`](DeepLearningBasic/2-3-cpu-gpu-device와-to-device.md)
- [Shape·Device 오류 디버깅](DeepLearningBasic/2-4-shape-device-오류-디버깅.md)

### Part 3. 퍼셉트론과 MLP 구조

- [퍼셉트론과 선형 결정 경계](DeepLearningBasic/3-1-퍼셉트론과-선형-결정-경계.md)
- [MLP의 입력층·은닉층·출력층](DeepLearningBasic/3-2-mlp-입력층-은닉층-출력층.md)
- [가중치·편향과 `nn.Linear`](DeepLearningBasic/3-3-가중치-편향과-nn-linear.md)
- [입출력 차원 계산과 Flatten](DeepLearningBasic/3-4-입출력-차원-계산과-flatten.md)
- [MLP Forward 미니 구현](DeepLearningBasic/3-5-mlp-forward-미니-구현.md)

### Part 4. 활성화 함수와 분류 출력층

- [비선형성과 활성화 함수의 필요성](DeepLearningBasic/4-1-비선형성과-활성화-함수-필요성.md)
- [ReLU의 역할과 사용 위치](DeepLearningBasic/4-2-relu의-역할과-사용-위치.md)
- [Sigmoid와 이진 분류 출력층](DeepLearningBasic/4-3-sigmoid와-이진-분류-출력층.md)
- [Softmax와 다중 분류 출력층](DeepLearningBasic/4-4-softmax와-다중-분류-출력층.md)

### Part 5. 손실 함수와 Optimizer

- [손실 함수의 역할과 목표 함수](DeepLearningBasic/5-1-손실-함수의-역할과-목표-함수.md)
- [회귀·이진·다중 분류 손실 선택](DeepLearningBasic/5-2-회귀-이진-다중-분류-손실-선택.md)
- [SGD, Adam과 Learning Rate](DeepLearningBasic/5-3-sgd-adam과-learning-rate.md)
- [파라미터 업데이트 코드 흐름](DeepLearningBasic/5-4-파라미터-업데이트-코드-흐름.md)

### Part 6. Autograd와 Gradient 계산

- [계산 그래프와 Chain Rule](DeepLearningBasic/6-1-계산-그래프와-chain-rule.md)
- [`requires_grad`와 Tensor Gradient](DeepLearningBasic/6-2-requires-grad와-tensor-gradient.md)
- [`loss.backward()`와 `.grad` 확인](DeepLearningBasic/6-3-loss-backward와-grad-확인.md)
- [`zero_grad`, `backward`, `step` 순서](DeepLearningBasic/6-4-zero-grad-backward-step-순서.md)
- [Autograd 디버깅과 안전한 평가 코드](DeepLearningBasic/6-5-autograd-디버깅과-안전한-평가-코드.md)

### Part 7. 데이터 파이프라인

- [Dataset과 DataLoader 역할](DeepLearningBasic/7-1-dataset과-dataloader-역할.md)
- [TensorDataset과 Custom Dataset](DeepLearningBasic/7-2-tensordataset과-custom-dataset.md)
- [Transform과 전처리 흐름](DeepLearningBasic/7-3-transform과-전처리-흐름.md)
- [Batch Size, Shuffle과 Train·Valid·Test 분할](DeepLearningBasic/7-4-batch-size-shuffle과-train-valid-test-분할.md)

### Part 8. 모델 학습 Loop 완성

- [MLP 모델과 Train·Validation Loop](DeepLearningBasic/8-1-8-5-mlp-모델과-train-validation-loop.md)
- [Accuracy와 Metric 누적](DeepLearningBasic/8-6-accuracy와-metric-누적.md)
- [MLP 종합 실습](DeepLearningBasic/8-8-mlp-종합-실습.md)

### Part 9. 재현성과 실험 관리

- [Seed 고정과 Logging 설계](DeepLearningBasic/9-1-9-2-seed-고정과-logging-설계.md)


## 딥러닝 심화
