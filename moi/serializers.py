from rest_framework import serializers

from moi.models import NetworkSliceSubnet
from moi.models import NsInfo
from moi.models import PLMNIdList
from moi.models import PerfRequirements
from moi.models import SNSSAIList
from moi.models import SST
from moi.models import SliceProfileList
from moi.models import AMFSet
from moi.models import AMFRegion
from moi.models import AMFRegionRelated
from moi.models import AMFSetRelated
from moi.models import AMFFunction
from moi.models import SMFFunction
from moi.models import UPFFunction
from moi.models import PCFunction
from moi.models import OtherFunction


class SSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = SST
        fields = ('value', 'type', 'characteristics')


class SNSSAIListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SNSSAIList
        fields = ('id', 'sST', 'sD')


class PLMNIdListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PLMNIdList
        fields = ('pLMNId', 'mcc', 'mnc', 'MobileNetworkOperator')


class PerfRequirementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfRequirements
        fields = ('id', 'scenario', 'experiencedDataRateDL',
                  'experiencedDataRateUL', 'areaTrafficCapacityDL', 'areaTrafficCapacityUL',
                  'overallUserDensity', 'activityFactor', 'ueSpeed', 'coverage')


class SliceProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliceProfileList
        fields = ('id', 'sNSSAIListId', 'pLMNIdList', 'perfReqId')


class NsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NsInfo
        fields = '__all__'


class NetworkSliceSubnetSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkSliceSubnet
        fields = ('nssiId', 'mFIdList', 'constituentNSSIIdList',
                  "operationalState", 'administrativeState', 'nsInfo', 'sliceProfileList')


class AMFSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMFSet
        fields = '__all__'


class AMFRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMFRegion
        fields = '__all__'


class AMFRegionRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMFRegionRelated
        fields = '__all__'


class AMFSetRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMFSetRelated
        fields = '__all__'


class AMFFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMFFunction
        fields = '__all__'


class SMFFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMFFunction
        fields = '__all__'


class UPFFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPFFunction
        fields = '__all__'


class PCFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PCFunction
        fields = '__all__'


class OtherFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherFunction
        fields = '__all__'


class NsInfoTopologySerializer(serializers.ModelSerializer):
    class Meta:
        model = NsInfo
        fields = ['id', 'nsInstanceDescription', 'nsdId', 'nsdInfoId', 'vnfInstance']


class NetworkSliceSubnetTopologySerializer(serializers.ModelSerializer):
    # sliceProfileList = SliceProfileListSerializer(many=True, read_only=True)
    nsInfo = NsInfoTopologySerializer(read_only=True)

    class Meta:
        model = NetworkSliceSubnet
        fields = ['nssiId', 'nsInfo']

